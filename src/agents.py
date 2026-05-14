"""LLM agent with tool-calling for flight and shopping search."""

from __future__ import annotations

from datetime import date
from typing import Any

from anthropic import Anthropic
from anthropic.types import TextBlock, ToolUseBlock
from openai import OpenAI

from .config import Config
from .tools.serpapi import search_flights, search_shopping

TODAY = date.today()  # 2026-05-12

SYSTEM_PROMPT = f"""Bạn là Tara Bot — một agent thông minh chuyên tìm kiếm chuyến bay và săn giá đồ.

NGUYÊN TẮC:
- Trả lời bằng tiếng Việt tự nhiên, thân thiện.
- Khi user hỏi vé máy bay, gọi tool search_flights.
- Khi user hỏi giá sản phẩm, gọi tool search_shopping.
- Sau khi tool trả kết quả, chuyển tiếp NGUYÊN VĂN kết quả đó cho user, chỉ thêm 1-2 câu ngắn ở đầu hoặc cuối.
- KHÔNG reformat lại kết quả từ tool — giữ nguyên định dạng.
- Có thể nói chuyện thông thường (chào hỏi, tạm biệt) — không cần gọi tool.

Hôm nay là {TODAY.strftime("%A, %d/%m/%Y")} — ĐÂY LÀ MỐC THỜI GIAN HIỆN TẠI.
Mặc định cho các câu hỏi mơ hồ về thời gian:
- "cuối tuần" → thứ Sáu tuần gần nhất (không quá khứ)
- "tuần sau" → tuần tiếp theo
- Nếu không rõ, lấy ngày đi và ngày về hợp lý."""

FLIGHT_TOOL: dict[str, Any] = {
    "name": "search_flights",
    "description": "Tìm chuyến bay. Trả về giá, hãng, giờ bay.",
    "input_schema": {
        "type": "object",
        "properties": {
            "departure_id": {
                "type": "string",
                "description": "Mã sân bay đi (IATA). Mặc định SGN",
            },
            "arrival_id": {
                "type": "string",
                "description": "Mã sân bay đến (IATA)",
            },
            "outbound_date": {
                "type": "string",
                "description": "Ngày đi (YYYY-MM-DD). Mặc định thứ 6 tuần sau.",
            },
            "return_date": {
                "type": "string",
                "description": "Ngày về (YYYY-MM-DD). Mặc định đi + 5 ngày.",
            },
            "adults": {
                "type": "integer",
                "description": "Số người lớn. Mặc định 1.",
            },
        },
        "required": ["arrival_id"],
    },
}

SHOPPING_TOOL: dict[str, Any] = {
    "name": "search_shopping",
    "description": "Tìm sản phẩm, so sánh giá. Hữu ích khi user hỏi về giá đồ.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Tên sản phẩm cần tìm (VD: iPhone 16, máy lọc không khí)",
            },
        },
        "required": ["query"],
    },
}

ALL_TOOLS = [FLIGHT_TOOL, SHOPPING_TOOL]

TOOL_FUNCTIONS: dict[str, Any] = {
    "search_flights": search_flights,
    "search_shopping": search_shopping,
}


class Agent:
    def __init__(self):
        self.mode = Config.llm_mode or "anthropic"
        self.system = SYSTEM_PROMPT
        self.history: list[dict[str, str]] = []

        if self.mode == "openai":
            if not Config.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set")
            self.client = OpenAI(
                api_key=Config.openai_api_key,
                base_url=Config.openai_base_url or None,
            )
            self.model = Config.openai_model or "gemini-2.5-flash"
        else:
            if not Config.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            self.client = Anthropic(api_key=Config.anthropic_api_key)
            self.model = "claude-sonnet-4-6"

    def chat(self, user_message: str) -> str:
        messages = list(self.history)
        messages.append({"role": "user", "content": user_message})

        for _ in range(5):
            if self.mode == "openai":
                response = self._call_openai(messages)
                reply_text, tool_calls = self._parse_openai_response(response)
                if not tool_calls:
                    self._save_history(user_message, reply_text)
                    return reply_text

                assistant_message = {
                    "role": "assistant",
                    "content": reply_text or None,
                    "tool_calls": tool_calls,
                }
                messages.append(assistant_message)

                for tool_call in tool_calls:
                    result = self._execute_tool_name(
                        tool_call["function"]["name"],
                        tool_call["function"]["arguments"],
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": result,
                        }
                    )
                continue

            response = self._call_anthropic(messages)
            content_blocks = response.content
            reply_text = ""
            tool_use_blocks = []

            for block in content_blocks:
                if isinstance(block, TextBlock):
                    reply_text += block.text
                elif isinstance(block, ToolUseBlock):
                    tool_use_blocks.append(block)

            if not tool_use_blocks:
                self._save_history(user_message, reply_text)
                return reply_text

            tool_results = []
            for block in tool_use_blocks:
                result = self._execute_tool(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

            messages.append({"role": "assistant", "content": content_blocks})
            messages.append({"role": "user", "content": tool_results})

        return "Xin lỗi, em không thể xử lý yêu cầu này ngay bây giờ. Thử lại với câu hỏi đơn giản hơn nhé!"

    def _save_history(self, user_message: str, reply_text: str) -> None:
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": reply_text})

    def _call_anthropic(self, messages: list[dict[str, Any]]) -> Any:
        import time

        for attempt in range(3):
            try:
                return self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    system=self.system,
                    messages=messages,
                    tools=ALL_TOOLS,
                )
            except Exception as exc:
                err = str(exc)
                if "429" in err or "rate_limit" in err.lower():
                    time.sleep(30 * (attempt + 1))
                    continue
                raise
        raise Exception("Anthropic API: rate limit exceeded after 3 retries")

    def _call_openai(self, messages: list[dict[str, Any]]) -> Any:
        import time

        tool_defs = [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"],
                },
            }
            for tool in ALL_TOOLS
        ]

        for attempt in range(3):
            try:
                return self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": self.system}] + messages,
                    tools=tool_defs,
                    temperature=0.2,
                )
            except Exception as exc:
                err = str(exc)
                if "429" in err or "rate_limit" in err.lower():
                    time.sleep(30 * (attempt + 1))
                    continue
                raise
        raise Exception("OpenAI-compatible API: rate limit exceeded after 3 retries")

    def _parse_openai_response(self, response: Any) -> tuple[str, list[dict[str, Any]]]:
        choice = response.choices[0]
        message = choice.message
        reply_text = message.content or ""
        tool_calls = []
        for tool_call in getattr(message, "tool_calls", None) or []:
            tool_calls.append(
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments or "{}",
                    },
                }
            )
        return reply_text, tool_calls

    def _execute_tool(self, name: str, args: Any) -> str:
        fn = TOOL_FUNCTIONS.get(name)
        if not fn:
            return f"Unknown tool: {name}"
        if isinstance(args, str):
            import json

            try:
                parsed_args = json.loads(args) if args else {}
            except Exception:
                parsed_args = {}
        else:
            parsed_args = dict(args)
        try:
            return fn(**parsed_args)
        except Exception as e:
            return f"Lỗi khi chạy {name}: {e}"

    def _execute_tool_name(self, name: str, args: str) -> str:
        return self._execute_tool(name, args)

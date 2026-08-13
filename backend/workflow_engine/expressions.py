class ExpressionEvaluator:

    def evaluate(
        self,
        expression: str,
        context: dict,
    ) -> bool:

        expression = expression.strip()

        if not expression:
            return True

        try:

            return bool(
                eval(
                    expression,
                    {
                        "__builtins__": {}
                    },
                    context,
                )
            )

        except Exception as exc:

            raise ValueError(
                f"Invalid expression: {expression}"
            ) from exc
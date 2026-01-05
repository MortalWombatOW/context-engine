# Philosophy: Human-Engaged Agentic Coding

ContextEngine serves as a bridge between AI coding assistants and structured workflows that encourage meaningful human-AI collaboration.

## The Problem with Full Automation

As AI coding agents become more powerful, there is a risk of users becoming "passengers" in their own projects. "Vibe coding"—where users approve changes without understanding them—can lead to unmaintainable codebases and a loss of conceptual integrity.

## The Solution: Structured Engagement

ContextEngine enforces a balanced approach:
*   **Mental Modeling**: The `/start` workflow ensures the agent understands the *whole* project before starting.
*   **Architectural Planning**: The `/plan` workflow forces a pause to plan before coding.
*   **Documentation as Code**: The `log_progress` tool ensures every step is recorded, creating an audit trail that keeps the human in the loop.

## Why "Context"?

The engine is named "ContextEngine" because its primary job is to manage the *context* (files, rules, history) passed to the LLM. By curating this context through structured workflows, we ensure the model acts as a focused expert rather than a generalist guesser.

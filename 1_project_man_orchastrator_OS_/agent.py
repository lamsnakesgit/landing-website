import os
import logging
from google.antigravity import Agent, LocalAgentConfig, types

logger = logging.getLogger(__name__)

async def run_agent_task(prompt: str) -> str:
    """
    Spawns an Antigravity agent to handle a task.
    We configure it to use our local LiteLLM Gateway instead of direct API.
    """
    
    # Normally, Antigravity connects directly. To route through LiteLLM,
    # we override the base_url or use OpenAI compatibility mode if supported,
    # or just use the model string that LiteLLM expects.
    # Note: Antigravity SDK by default expects Gemini. If LiteLLM exposes Gemini API,
    # we can just point the client endpoint there.
    # For now, we will assume standard configuration and set GEMINI_API_KEY.
    
    # Ensure subagents are enabled for complex orchestration
    capabilities = types.CapabilitiesConfig(
        enable_subagents=True,
    )
    
    # We use a custom model string if using LiteLLM (e.g. models/antigravity-pro)
    # The SDK allows defining model strings. 
    # If the SDK strictly requires a direct connection, LiteLLM acts as a transparent proxy.
    
    config = LocalAgentConfig(
        system_instructions=(
            "You are an autonomous AI Orchestrator Worker. "
            "Your job is to receive tasks, write code, analyze data, and potentially create GitHub PRs. "
            "You run in an isolated environment and have access to various tools."
        ),
        capabilities=capabilities,
        # model="models/gemini-1.5-pro" # Example standard usage
    )

    logger.info("Initializing Agent session...")
    
    # In a real environment, you might inject MCP tools (e.g., github-mcp) here.
    async with Agent(config) as agent:
        logger.info(f"Agent executing prompt: {prompt}")
        response = await agent.chat(prompt)
        result_text = await response.text()
        logger.info("Agent execution completed.")
        return result_text

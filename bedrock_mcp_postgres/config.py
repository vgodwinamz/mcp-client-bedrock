# config.py
import os
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger("mcp-bedrock-client")

def load_mcp_config() -> Dict:
    """Load MCP server configurations from the config file"""
    config_path = os.path.expanduser("./bedrock_mcp_postgres/mcp.json")
    servers = {}
    
    # Verify config file exists
    if os.path.exists(config_path):
        # Load config to get server URLs
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if "mcpServers" in config:
                for server_name, server_config in config["mcpServers"].items():
                    args = server_config.get("args", [])
                    if len(args) > 1:
                        server_url = args[1]
                        logger.info(f"Found server {server_name} with URL: {server_url}")
                        servers[server_name] = server_url
                    else:
                        logger.warning(f"Could not find URL for server {server_name} in MCP config")
            else:
                logger.warning("No MCP servers found in config")
        except Exception as e:
            logger.error(f"Error loading MCP config: {str(e)}")
    else:
        logger.warning(f"MCP config file not found at {config_path}")
    
    return servers

def save_server_to_config(server_name: str, server_url: str, command: str = "npx", 
                         transport: str = "sse-only", allow_http: bool = False) -> bool:
    """Add a new server to the MCP configuration file"""
    config_path = os.path.expanduser("./bedrock_mcp_postgres/mcp.json")
    
    try:
        # Create config file if it doesn't exist
        if not os.path.exists(config_path):
            config = {"mcpServers": {}}
        else:
            # Load existing config
            with open(config_path, 'r') as f:
                config = json.load(f)
                if "mcpServers" not in config:
                    config["mcpServers"] = {}
        
        # Prepare args array
        args = ["mcp-remote", server_url, "--transport", transport]
        
        # Add --allow-http flag if needed
        if allow_http or server_url.startswith("http://"):
            args.append("--allow-http")
        
        # Add or update server configuration
        config["mcpServers"][server_name] = {
            "command": command,
            "args": args
        }
        
        # Write updated config back to file
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Added/updated server {server_name} with URL: {server_url}")
        return True
    except Exception as e:
        logger.error(f"Error saving server to MCP config: {str(e)}")
        return False
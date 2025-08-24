# Logs directory
This directory contains log files for the AWS Learning Agent.

## Log Files

- `agent.log` - Main application logs
- `api.log` - API server logs  
- `streamlit.log` - Web UI logs
- `errors.log` - Error-specific logs

## Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about application flow
- **WARNING**: Warning messages for attention
- **ERROR**: Error messages for issues
- **CRITICAL**: Critical errors that may stop the application

## Log Rotation

Logs are automatically rotated when they reach certain size limits to prevent disk space issues.

## Viewing Logs

```bash
# View real-time logs
tail -f logs/agent.log

# Search for specific errors
grep "ERROR" logs/agent.log

# View last 100 lines
tail -100 logs/agent.log
```
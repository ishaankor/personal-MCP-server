# Ishaan Koradia - Personal MCP Server

A remote Model Context Protocol (MCP) server that provides information about me via StreamableHTTP -- Ishaan Koradia, an aspiring AI/ML Engineer and undergraduate student at UC San Diego. 

## About

This MCP server allows my personal AI chatbot to access structured information about me from my bio, achievements, skills, and contact information. As a backend for [my personal website](https://github.com/ishaankor/my-personal-website), it provides a standardized way to share personal and professional details through the MCP protocol that's both secure and optimal.

## Features

- **Personal Information**: Bio, education, and background details
- **Professional Achievements**: Projects like Transformi, Daily Motivation, and NotesTaker
- **Skills & Expertise**: Python, JavaScript, ML, Data Science, and more
- **Contact Information**: GitHub, LinkedIn, and email
- **MCP Protocol Compliance**: Standard protocol for AI model context

## Tech Stack

- **Backend**: Python with FastAPI
- **Protocol**: Model Context Protocol (MCP)
- **Deployment**: Render.com
- **Data**: Structured text files

## Deployment

This project is configured for deployment on Render.com using the provided `render.yaml` configuration.

## API Endpoints

The server implements the MCP protocol by utilizing roots/resources and tool callings for accessing personal information:

- `/mcp/resources` - Available resources and data
- `/mcp/tools` - Available tools and functions

### Connect
- GitHub: [ishaankor](https://github.com/ishaankor)
- LinkedIn: [ishaankoradia](https://linkedin.com/in/ishaankoradia)
- Email: ishaankor@gmail.com

## Contributing

This is a personal project, but feedback and suggestions are welcome! Feel free to open an issue or reach out directly.

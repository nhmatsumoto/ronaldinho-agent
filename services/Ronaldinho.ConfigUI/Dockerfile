# Use the official Bun image
FROM oven/bun:1

WORKDIR /app

# Copy dependency files and install optimally
COPY package.json bun.lock ./
RUN bun install

# Copy source code
COPY . .

# Expose Vite dev port
EXPOSE 5173

# Serve using Vite's development server for hot-reloading
CMD ["bunx", "--bun", "vite", "--host", "0.0.0.0"]

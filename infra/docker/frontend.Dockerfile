FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

# Copy workspace configuration
COPY package.json ./
COPY pnpm-workspace.yaml ./

# Copy all package.json files to maintain workspace structure
COPY apps/frontend/package*.json ./apps/frontend/
COPY packages/ts-utils/package*.json ./packages/ts-utils/

# Install dependencies for the entire workspace
RUN corepack enable pnpm && pnpm install --frozen-lockfile || pnpm install

# Development stage
FROM base AS development
WORKDIR /app

# Copy entire workspace structure from deps
COPY --from=deps /app ./

# Copy fresh source code (this will overwrite only the source files, not node_modules)
COPY apps/frontend ./apps/frontend
COPY packages/ts-utils ./packages/ts-utils

# Set working directory to the frontend app
WORKDIR /app/apps/frontend

# Expose port
EXPOSE 3000

# Set environment to development
ENV NODE_ENV=development

# Start the development server
CMD ["npm", "run", "dev"]

# Production builder stage
FROM base AS builder
WORKDIR /app

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/packages ./packages

# Copy source code
COPY apps/frontend ./
COPY packages/ts-utils ./packages/ts-utils

# Set environment to production
ENV NODE_ENV=production

# Build the application
RUN npm run build

# Production stage
FROM base AS production
WORKDIR /app

ENV NODE_ENV=production

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next

# Copy public assets if they exist
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
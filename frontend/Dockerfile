# Change this line from node:18-alpine to node:20-alpine
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Build the Next.js app for production
RUN npm run build

# Expose the port
EXPOSE 3000

# Start the app
CMD ["npm", "start"]
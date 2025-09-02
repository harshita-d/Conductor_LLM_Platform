# Use official Node image
FROM node:18

# Set working directory
WORKDIR /app

# Copy only package.json and install dependencies first
COPY package*.json ./
RUN npm install

# Copy all source code (after installing deps for better caching)
COPY . .

# Expose port used by React dev server
EXPOSE 3000

# Start development server with hot reloading
CMD ["npm", "start"]

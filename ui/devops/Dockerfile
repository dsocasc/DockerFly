# Use the official Nginx image from Docker Hub
FROM nginx:latest

ARG EXPOSED_PORT=8000

# Copy custom HTML file to the Nginx web folder
COPY ./src/index.html /usr/share/nginx/html/index.html
COPY ./src/script.js /usr/share/nginx/html/script.js
COPY ./src/styles.css /usr/share/nginx/html/styles.css
COPY ./src/favicon.ico /usr/share/nginx/html/favicon.ico

# Expose port 80
EXPOSE 80

# Set environment variables for Nginx
ENV VIRTUAL_HOST="dockerfly.nimbus.net"
ENV VIRTUAL_PORT=80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
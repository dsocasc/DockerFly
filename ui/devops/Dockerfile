# Use the official Nginx image from Docker Hub
FROM nginx:latest

ARG URL=""

# Copy custom HTML file to the Nginx web folder
COPY ./src/index.html /usr/share/nginx/html/index.html
COPY ./src/script.js /usr/share/nginx/html/script.js
COPY ./src/styles.css /usr/share/nginx/html/styles.css
COPY ./src/favicon.ico /usr/share/nginx/html/favicon.ico
COPY ./src/icon.png /usr/share/nginx/html/icon.png
COPY ./resources/config.yml /usr/share/nginx/html/config.yml

# Expose port 80
EXPOSE 80

# Set environment variables for Nginx
ENV VIRTUAL_HOST=${URL}
ENV VIRTUAL_PORT=80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
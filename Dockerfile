FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/portfolio.conf

# Copy ALL static files (html + css + js + seo files)
COPY index.html  /usr/share/nginx/html/index.html
COPY styles.css  /usr/share/nginx/html/styles.css
COPY script.js   /usr/share/nginx/html/script.js
COPY robots.txt  /usr/share/nginx/html/robots.txt
COPY sitemap.xml /usr/share/nginx/html/sitemap.xml

# Validate nginx config at build time
RUN nginx -t

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

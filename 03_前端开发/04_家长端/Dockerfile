FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build:h5
RUN chunk=$(find /app/dist/js -maxdepth 1 -type f -name '*.js' ! -name 'app.js' ! -name '*.LICENSE.txt' | sort | head -n 1 | xargs -n 1 basename) && \
    printf '%s\n' '<!DOCTYPE html>' '<html lang="zh-CN">' '<head>' '  <meta charset="UTF-8">' '  <meta name="viewport" content="width=device-width, initial-scale=1.0">' '  <title>OPENEXAM 家长端</title>' '  <link rel="stylesheet" href="/css/app.css">' '</head>' '<body>' '  <div id="app"></div>' "  <script src=\"/js/${chunk}\"></script>" '  <script src="/js/app.js"></script>' '</body>' '</html>' > /app/dist/index.html

FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

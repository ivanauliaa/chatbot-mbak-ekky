FROM node:18-alpine

RUN npm install -g http-server

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npx browserslist@latest --update-db

RUN npm run build

EXPOSE 8080
CMD [ "http-server", "dist" ]

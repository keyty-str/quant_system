# 使用Node.js 18作为基础镜像
FROM node:18-alpine as builder

# 设置工作目录
WORKDIR /app

# 设置淘宝镜像
RUN npm config set registry https://registry.npmmirror.com

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# 使用Nginx作为生产镜像
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/build /usr/share/nginx/html

# 复制Nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 3000

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]
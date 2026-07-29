# 技术栈文档

## 1. 核心技术栈

| 类别 | 技术 | 版本 | 选择理由 |
|------|------|------|----------|
| 框架 | Next.js | 14.x | App Router全栈框架，SSR+API一体 |
| 前端库 | React | 18.x | Next.js内置，生态成熟 |
| 语言 | TypeScript | 5.x | 类型安全，开发体验好 |
| 样式 | TailwindCSS | 3.x | 原子化CSS，快速开发，无需写CSS文件 |
| 数据库 | SQLite | 3.x | 零配置，单文件，单机部署完美 |
| ORM | Prisma | 5.x | 类型安全，迁移管理，开发体验好 |
| 认证 | jose | 5.x | JWT签发/验证，轻量无依赖 |
| 密码 | bcryptjs | 2.x | 密码哈希，纯JS实现无需编译 |
| AI | @aws-sdk/client-bedrock-runtime | latest | Bedrock SDK调用 |
| AI | @aws-sdk/client-bedrock | latest | 模型列表获取 |

## 2. 前端辅助库

| 类别 | 技术 | 选择理由 |
|------|------|----------|
| 图表 | Recharts | React原生图表，API简单 |
| 图标 | lucide-react | 现代图标库，体积小 |
| 表单 | react-hook-form | 轻量表单管理 |
| 数据导出 | xlsx | Excel导出（sheetjs） |
| HTTP客户端 | fetch (内置) | 无需额外库 |
| 日期 | date-fns | 轻量日期处理 |
| Toast通知 | react-hot-toast | 简单好用的Toast |

## 3. 开发工具

| 类别 | 技术 | 用途 |
|------|------|------|
| 包管理 | npm | Node.js默认包管理 |
| 代码规范 | ESLint | Next.js内置配置 |
| 格式化 | Prettier | 代码格式统一 |
| 数据库管理 | Prisma Studio | 可视化数据库浏览 |

## 4. 项目配置

### package.json 关键依赖

```json
{
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "@prisma/client": "^5.15.0",
    "@aws-sdk/client-bedrock": "^3.600.0",
    "@aws-sdk/client-bedrock-runtime": "^3.600.0",
    "jose": "^5.6.0",
    "bcryptjs": "^2.4.3",
    "recharts": "^2.12.0",
    "lucide-react": "^0.400.0",
    "react-hook-form": "^7.52.0",
    "react-hot-toast": "^2.4.0",
    "date-fns": "^3.6.0",
    "xlsx": "^0.18.5"
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "prisma": "^5.15.0",
    "@types/react": "^18.3.0",
    "@types/node": "^20.14.0",
    "@types/bcryptjs": "^2.4.6",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^8.57.0",
    "eslint-config-next": "^14.2.0"
  }
}
```

### 启动命令

```bash
npm install          # 安装依赖
npx prisma generate  # 生成Prisma Client
npx prisma db push   # 创建数据库表
npx prisma db seed   # 填充种子数据
npm run dev          # 启动开发服务器 (localhost:3000)
```

## 5. 约束与替代方案

| 约束 | 当前选择 | 替代方案 | 不选择的原因 |
|------|----------|----------|-------------|
| 单机部署 | SQLite | PostgreSQL | 需要额外安装数据库服务 |
| 快速开发 | Next.js全栈 | 前后端分离(React+Express) | 多项目维护复杂 |
| 认证 | 自研JWT | NextAuth.js | NextAuth配置复杂，不需要OAuth |
| 状态管理 | Context+fetch | Redux/Zustand | 项目不复杂，无需全局状态管理 |
| 图表 | Recharts | ECharts/D3 | ECharts体积大，D3学习成本高 |
| CSS | TailwindCSS | CSS Modules/Styled | Tailwind开发最快 |

## 6. SQLite WAL模式配置

SQLite默认为顺序写入，启用WAL模式提升并发性能：

```typescript
// prisma/schema.prisma 中无需额外配置
// 在应用启动时执行:
// PRAGMA journal_mode = WAL;
// PRAGMA busy_timeout = 5000;
```

这样可以支持并发读取，写入时通过busy_timeout等待而非立即失败。

# Alembic — 数据库迁移工具使用指南

## 1. 什么是 Alembic

Alembic 是 SQLAlchemy 官方出品的**数据库迁移（Migration）工具**，用于管理数据库表结构的版本变更。它能像 Git 管理代码一样管理数据库结构的演进历史。

## 2. 为什么要用 Alembic

在实际项目中，数据库表结构会随着需求不断变化（新增字段、修改类型、增加索引等），Alembic 可以：

- **追踪变更**：记录每次数据库结构的修改历史
- **版本回滚**：可以回退到任意历史版本
- **团队协作**：将表结构变更纳入版本控制，团队成员同步执行
- **自动化部署**：在 CI/CD 流程中自动执行数据库迁移
- **避免破坏性操作**：先定义脚本，检查通过后再执行

## 3. 核心概念

| 概念 | 说明 |
|------|------|
| **Migration（迁移）** | 一次数据库结构的变更脚本 |
| **Revision（版本）** | 每个迁移都有一个唯一的版本 ID |
| **Upgrade** | 升级到新版本（向前迁移） |
| **Downgrade** | 回退到旧版本（向后迁移） |
| **alembic.ini** | Alembic 的主配置文件 |
| **env.py** | 迁移环境配置，连接数据库和模型 |
| **versions/** | 存放所有迁移脚本的目录 |

## 4. 安装

```bash
pip install alembic
```

## 5. 初始化 Alembic

在项目根目录执行：

```bash
alembic init migrations
```

会生成以下目录结构：

```
migrations/
├── alembic.ini          # 配置数据库连接
├── env.py               # 迁移环境（需手动配置）
├── script.py.mako       # 迁移脚本模板
└── versions/            # 存放迁移脚本
```

## 6. 配置步骤

### 6.1 修改 `alembic.ini` 中的数据库连接

```ini
sqlalchemy.url = postgresql+asyncpg://postgres:password@localhost:5432/bookly_db
```

### 6.2 修改 `env.py` 导入模型元数据

```python
from src.books.models import Book
from sqlmodel import SQLModel

target_metadata = SQLModel.metadata
```

## 7. 常用命令

| 命令 | 说明 |
|------|------|
| `alembic init migrations` | 初始化 Alembic |
| `alembic revision --autogenerate -m "描述"` | 自动生成迁移脚本 |
| `alembic upgrade head` | 升级到最新版本 |
| `alembic downgrade -1` | 回退一个版本 |
| `alembic history` | 查看迁移历史 |
| `alembic current` | 查看当前版本 |
| `alembic stamp head` | 标记当前数据库为最新版本（不执行迁移） |

## 8. 工作流程

```
1. 修改 models.py 模型定义
        ↓
2. alembic revision --autogenerate -m "add new field"
        ↓
3. 检查 versions/ 下的迁移脚本是否正确
        ↓
4. alembic upgrade head  (执行迁移)
        ↓
5. 提交迁移脚本到 Git （团队同步）
```

## 9. 注意事项

- **始终检查自动生成的脚本**：`--autogenerate` 无法检测所有变更（如重命名列）
- **不要手动修改已执行的迁移脚本**：已执行的版本是只读的
- **迁移脚本纳入版本控制**：`versions/` 目录必须提交到 Git
- **生产环境谨慎执行**：`downgrade` 可能导致数据丢失

## 10. 示例迁移脚本

```python
# migrations/versions/33e9f86c67bf_init.py
import sqlalchemy as sa
from alembic import op

revision = '33e9f86c67bf'
down_revision = None  # 第一个版本，无父版本

def upgrade():
    op.create_table(
        'books',
        sa.Column('uid', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('author', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('uid')
    )

def downgrade():
    op.drop_table('books')
```
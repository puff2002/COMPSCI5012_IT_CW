# IT Group Work Project Design

### **1. 核心功能描述 (Core Functional Descriptions)**

1. **用户档案 (User Profile & Auth):**
   1. 用户注册时可选输入昵称、身高、体重（满足用户输入被存储的要求）。
   2. 数据存储在 User 表中。
   3. 用户可绑定第三方账号如 Google / Apple ，用于 登录、直接同步健康（身高体重数据）
2. **衣物数字化 (Digital Inventory - CRUD):**
   1. **增 (Create):** 上传图片，并选择两个关键属性：**分类**（Type: 上装/下装/裙子/配饰）和 **季节**（Season: 春夏秋冬）。
   2. **查 (Read):** 按季节或分类筛选查看衣柜。
   3. **删/改 (Update/Delete):** 更新/删除已有的衣物。
3. **智能穿搭 (Smart Styling):**
   1. **逻辑:** 从数据库中随机抽取一件“上装”和一件“下装”（或单件“全身/裙子”），并根据当前选择的“季节”进行过滤。
   2. AI：使用 LLM 进行穿搭推荐
4. **穿搭日记 (Outfit Log):**
   1. 用户确认某套穿搭后，将其保存到历史记录表，记录穿搭日期。
   2. 拍照记录穿搭，使用机器学习匹配穿搭并记录
   3. 用户可以手工修改/修正穿搭日志

### **2. 用户故事 Specification**

* **M1 (Authentication):**

**As a** new user,

**I want** to register an account with my nickname, height, and weight,

**so that** I can create a private space to manage my personal wardrobe.

（满足要求：用户认证 & 数据输入 ）

* **M2 (Input/Inventory):**

**As a** user,

**I want** to upload a clothing photo and select its category (e.g., Long-sleeve, Skirt) and season,

**so that** I can build a searchable digital inventory of my clothes.

（满足要求：数据库交互 & 用户输入被应用 ）

* **M3 (View/Filter):**

**As a** user,

**I want** to view my clothes filtered by "Season" (e.g., Summer) or "Type",

**so that** I can quickly find relevant items without looking through my whole closet.

（满足要求：与数据库模型交互 ）

* **M4 (Manage):**

**As a** user,

**I want** to edit details or delete items I no longer own,

**so that** my digital closet accurately reflects my physical wardrobe.

**Should Have** *（自动穿搭）*

* **S1 (Functionality):**

**As a** user who is in a rush,

**I want** to click a "Generate Outfit" button to get a random valid combination (Top + Bottom),

**so that** I can get a dressing suggestion instantly without thinking.

* **S2 (History):**

**As a** user,

**I want** to save a generated outfit to my "History Log",

**so that** I can remember what I wore recently and avoid repeating the same look.

#### **Could Have**

* **C1 (External API):**

**As a** user,

**I want** the app to automatically suggest outfits based on the current local temperature,

**so that** I don't wear a t-shirt on a freezing winter day.

#### **Won't Have**

* **W1:**

**As a** user,

**I want** to use AR (Augmented Reality) to virtually try on the clothes on my 3D avatar.

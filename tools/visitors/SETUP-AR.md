# إعداد سجل الزوار ولوحة المؤسس (مرة واحدة بس)

كل ده مجاني (خطة Supabase المجانية). محتاج حوالي 10 دقايق.

## 1) اعمل حساب ومشروع على Supabase
1. افتح https://supabase.com واضغط **Start your project**، وسجّل دخول (بحساب GitHub أو بالإيميل).
2. اضغط **New project**:
   - **Name**: مثلًا `grade12-visitors`
   - **Database Password**: اكتب كلمة سر قوية واحفظها عندك (ما تبعتهاش لحد).
   - **Region**: اختار أقرب مكان لمصر، مثلًا **Central EU (Frankfurt)**.
   - الخطة: **Free**.
3. اضغط **Create new project** واستنى دقيقتين لحد ما المشروع يجهز.

## 2) شغّل ملف قاعدة البيانات
1. من القايمة الشمال اختار **SQL Editor** ← **New query**.
2. افتح ملف `supabase-setup.sql`، وانسخ كل اللي فيه، والزقه هناك.
3. اضغط **Run**. المفروض يظهر **Success. No rows returned**.

## 3) اعمل حساب المؤسس (ده حسابك إنت بس)
1. من القايمة اختار **Authentication** ← **Users** ← **Add user** ← **Create new user**.
2. اكتب الإيميل بتاعك وكلمة سر قوية (دي اللي هتدخل بيها لوحة المؤسس)، وعلّم على **Auto Confirm User**، واضغط **Create user**.
3. ارجع لـ **SQL Editor** ← **New query**، والزق السطر ده بعد ما تحط إيميلك مكان المثال:
   ```sql
   insert into public.founders (user_id) select id from auth.users where email = 'your-email@example.com';
   ```
   اضغط **Run**. المفروض يظهر **Success** و **1 row affected**.

## 4) اقفل التسجيل لأي حد تاني
1. **Authentication** ← **Sign In / Providers** (أو **Settings**).
2. اقفل **Allow new users to sign up** واضغط **Save**.
   كده محدش يقدر يعمل حساب جديد غيرك.

## 5) هات العنوان والمفتاح العام
1. اضغط على علامة الترس **Project Settings**.
2. من **Data API** (أو **API**) انسخ **Project URL** (شكله `https://xxxx.supabase.co`).
3. من **API Keys** انسخ **Publishable key** (بيبدأ بـ `sb_publishable_`).
   - لو مش لاقيه، استخدم مفتاح **anon public** من **Legacy API Keys**.
4. ابعت الاتنين دول بس. دول عامّين ومعمولين علشان يتحطوا في الموقع.

## ممنوع تبعت أو تحط في الموقع
- **Secret key** (بيبدأ بـ `sb_secret_`) أو **service_role**.
- كلمة سر قاعدة البيانات.
- كلمة سر حساب المؤسس.

## بعد كده
- لوحة المؤسس: `founder.html` في الموقع، وتدخل بإيميل وكلمة سر حساب المؤسس.
- لو الموقع فضل 7 أيام من غير ولا زيارة، Supabase بيوقف المشروع مؤقتًا (Paused) في الخطة المجانية. البيانات **مش بتتمسح**، وترجّعه من لوحة Supabase بزرار **Resume**.

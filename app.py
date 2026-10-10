"""
اسم التطبيق: لوحة الإدارة المالية الذكية والتحليلية
المطور: مصعب العرجان
الوصف: تطبيق ويب تفاعلي مبني بـ Streamlit لإدارة النفقات وتحليل السلوك المالي، مصمم ليكون قابلاً للتطوير والتوسع مستقبلاً.
"""

import streamlit as st
import pandas as pd
import numpy as np

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="لوحة الإدارة المالية الذكية",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="expanded"
)

# تهيئة حالة الجلسة (Session State) لضمان استمرارية البيانات وثباتها أثناء التصفح
def init_session_state():
    if 'expenses' not in st.session_state:
        st.session_state.expenses = pd.DataFrame(columns=["التاريخ", "الفئة", "الوصف", "المبلغ"])
    if 'custom_categories' not in st.session_state:
        st.session_state.custom_categories = [
            "السكن والفواتير", 
            "المواد الغذائية", 
            "المواصلات والوقود", 
            "الترفيه", 
            "التعليم", 
            "أخرى"
        ]

init_session_state()

# عنوان وتصميم الواجهة
st.title("💎 لوحة التحكم والتحليل المالي المتقدم")
st.markdown("أداة هندسية رقمية لإدارة الميزانية الشخصية وتحليل سلوكيات الإنفاق بدقة عالية.")
st.markdown("---")

# الشريط الجانبي للإعدادات وإدخال البيانات
with st.sidebar:
    st.header("⚙️ الإعدادات والميزانية")
    monthly_income = st.number_input(
        "الدخل الشهري الإجمالي (دينار)",
        min_value=0.0,
        value=500.0,
        step=50.0,
        format="%.2f"
    )
    
    st.markdown("---")
    st.subheader("➕ إضافة مصروف جديد")
    
    # خيار إضافة فئة جديدة للتوسع المستقبلي
    new_cat_input = st.text_input("أضف فئة مخصصة جديدة (اختياري):")
    if new_cat_input and new_cat_input not in st.session_state.custom_categories:
        if st.button("حفظ الفئة الجديدة"):
            st.session_state.custom_categories.append(new_cat_input)
            st.success(f"تمت إضافة الفئة: {new_cat_input}")
            st.rerun()

    # استخدام Form لضمان سلاسة الإدخال على الموبايل وعدم حدوث Rerun مزعج مع كل حرف
    with st.form("expense_form", clear_on_submit=True):
        selected_category = st.selectbox("فئة المصروف", st.session_state.custom_categories)
        description = st.text_input("وصف المصروف", placeholder="مثال: فاتورة الإنترنت أو تسوق")
        amount = st.number_input("المبلغ (دينار)", min_value=0.1, value=10.0, step=1.0, format="%.2f")
        
        submit_button = st.form_submit_button("إضافة المصروف للسجل")
        
        if submit_button:
            current_date = pd.Timestamp.now().strftime("%Y-%m-%d")
            new_row = pd.DataFrame({
                "التاريخ": [current_date],
                "الفئة": [selected_category],
                "الوصف": [description if description else "بدون وصف"],
                "المبلغ": [amount]
            })
            st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
            st.success("تمت إضافة الحركة المالية بنجاح!")
            st.rerun()

# استرجاع البيانات الحالية وإجراء العمليات الحسابية
df_expenses = st.session_state.expenses
total_expenses = df_expenses["المبلغ"].sum() if not df_expenses.empty else 0.0
remaining_balance = monthly_income - total_expenses

# عرض المؤشرات العليا (Metrics)
col1, col2, col3 = st.columns(3)
col1.metric("الدخل الشهري", f"{monthly_income:,.2f} د.أ")
col2.metric("إجمالي المصروفات", f"{total_expenses:,.2f} د.أ", delta_color="inverse")
col3.metric("المتبقي للادخار", f"{remaining_balance:,.2f} د.أ")

# شريط التقدم والتنبيهات الذكية
if monthly_income > 0:
    spending_ratio = (total_expenses / monthly_income) * 100
    st.progress(min(int(spending_ratio), 100))
    
    if spending_ratio > 90:
        st.error(f"🚨 تحذير حرج: وصلت نسبة الاستهلاك إلى {spending_ratio:.1f}%! وضعك المالي يتطلب تدخلاً فورياً.")
    elif spending_ratio > 75:
        st.warning(f"⚠️ تنبيه: استهلكت {spending_ratio:.1f}% من إجمالي دخلك، اقتربت من الحد الأقصى.")
    elif spending_ratio > 50:
        st.info(f"⚡ إضاءة: لقد تجاوزت منتصف الدخل، نسبة المصروفات الحالية {spending_ratio:.1f}%.")
    else:
        st.success(f"✅ أداء ممتاز: نسبة المصروفات آمنة ومسيطر عليها تماماً ({spending_ratio:.1f}%).")

st.markdown("---")

# عرض المحتوى في تبويبات منظمة (Tabs)
if not df_expenses.empty:
    tab1, tab2, tab3 = st.tabs(["📊 التحليل الرسومي", "📋 السجل التفصيلي", "💾 إدارة وتصدير البيانات"])
    
    with tab1:
        st.subheader("توزيع النفقات حسب الفئات")
        grouped_df = df_expenses.groupby("الفئة")["المبلغ"].sum()
        st.bar_chart(grouped_df)
        
        # تحليل ذكي تلقائي
        highest_category = grouped_df.idxmax() if not grouped_df.empty else "لا يوجد"
        highest_amount = grouped_df.max() if not grouped_df.empty else 0
        st.info(f"💡 **رؤية تحليلية:** الفئة الأكثر استهلاكاً لسيولتك هي **({highest_category})** بإجمالي **{highest_amount:,.2f} دينار**.")

    with tab2:
        st.subheader("سجل الحركات المالية اليومية")
        st.dataframe(df_expenses, use_container_width=True)
        
    with tab3:
        st.subheader("خيارات تصدير وإدارة البيانات")
        
        # تصدير البيانات إلى ملف CSV
        csv_data = df_expenses.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 تحميل السجل كملف CSV",
            data=csv_data,
            file_name='my_financial_records.csv',
            mime='text/csv',
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ مسح وإعادة تعيين كافة البيانات"):
            st.session_state.expenses = pd.DataFrame(columns=["التاريخ", "الفئة", "الوصف", "المبلغ"])
            st.success("تم تفريغ السجل بنجاح.")
            st.rerun()
else:
    st.info("📌 لا توجد سجلات مالية مسجلة حتى الآن. استخدم الشريط الجانبي لإضافة أول مصروف.")

# [ملاحظة للمطور - قابلية التوسع]: 
# مستقبلًا، يمكنك استبدال st.session_state.expenses بقاعدة بيانات خفيفة مثل SQLite 
# لحفظ السجلات بشكل دائم حتى بعد إغلاق المتصفح.

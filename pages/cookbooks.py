import streamlit as st
from ozz_auth import all_page_auth_signin
from master_cookbook.cookbook_db import MealDatabase, Meal, CookbookDatabase, Cookbook, save_meal_image
from master_cookbook.cookbook_utils import (
    display_meals_grid,
    meal_search_sidebar,
    meal_form,
    cookbook_dashboard,
    import_recipe_from_url,
    manage_cookbooks_page,
    view_cookbook_detail,
    cookbook_form,
    extract_recipe_from_image,
)
from master_ozz.utils import ozz_master_root
import os
import streamlit_antd_components as sac
import pytesseract
from datetime import datetime
def sac_menu_buttons_func_other(items=['Browse Meals', 'My Cookbooks',  'Add Meal']):
    sac_menu_buttons = sac.buttons(
        items=items,
        index=0,
        format_func='title',
        align='center',
        direction='horizontal',
        radius='lg',
        # compact=False,
        return_index=False,
    )

    return sac_menu_buttons

def sac_menu_buttons_func(items=['Browse Meals', 'My Cookbooks',  'Add Meal']):
    return sac.menu([
        sac.MenuItem('Browse Meals', icon='search'),
        sac.MenuItem('My Cookbooks', icon='book'),
        sac.MenuItem('Add Meal', icon='plus-circle'),
    ], 
    format_func='title',
    open_all=True,
    return_index=False)

def main():
    s = datetime.now()

    st.set_page_config(
        page_title="Family Cooks", 
        layout="wide", 
        page_icon="🔪", 
        # initial_sidebar_state='collapsed',
    )
    auth_dict = all_page_auth_signin(page='cookbooks')
    authenticator = auth_dict['authenticator']

    query_params = st.query_params
    view_mode = query_params.get("view", None)

    # with st.sidebar:
    #     st.markdown("## 🔪 My Cookbook")
        # st.write(st.session_state.get('client_user'))

    page = sac_menu_buttons_func()

    # Initialize databases
    meals_db_path = os.path.join(ozz_master_root(), "master_cookbook", "meals_db")
    cookbooks_db_path = os.path.join(ozz_master_root(), "master_cookbook", "cookbooks_db")

    # WORKER needs update to support per-user DBs
    # user_email = st.session_state.get('username', 'guest')
    # meals_db_path = os.path.join(ozz_master_root(), "master_cookbook", "meals_db", user_email)
    # cookbooks_db_path = os.path.join(ozz_master_root(), "master_cookbook", "cookbooks_db", user_email)
    # Create user-specific directories if they don't exist
    # os.makedirs(meals_db_path, exist_ok=True)
    # os.makedirs(cookbooks_db_path, exist_ok=True)

    meal_db = MealDatabase(meals_db_path)
    cookbook_db = CookbookDatabase(cookbooks_db_path)
    
    # Check if we're editing a meal FIRST (before any other checks)
    if 'editing_meal_id' in st.session_state:
        meal_id = st.session_state['editing_meal_id']
        edit_meal = meal_db.get_meal(meal_id)
        
        if edit_meal:
            st.title(f"✏️ Edit Meal: {edit_meal.name}")
            
            if st.button("← Back to Browse"):
                del st.session_state['editing_meal_id']
                st.rerun()
            
            meal_form(meal_db, edit_meal=edit_meal, cookbook_db=cookbook_db)
            return  # Important: stop here, don't render the rest
    
    # Check if viewing a cookbook
    if 'viewing_cookbook_id' in st.session_state:
        cookbook_id = st.session_state['viewing_cookbook_id']
        cookbook = cookbook_db.get_cookbook(cookbook_id)
        
        if cookbook:
            view_cookbook_detail(cookbook, meal_db, cookbook_db)
            return
    
    # Check if editing a cookbook
    if 'editing_cookbook_id' in st.session_state:
        cookbook_id = st.session_state['editing_cookbook_id']
        edit_cookbook = cookbook_db.get_cookbook(cookbook_id)
        
        if edit_cookbook:
            st.title(f"✏️ Edit Cookbook: {edit_cookbook.name}")
            
            if st.button("← Back"):
                del st.session_state['editing_cookbook_id']
                st.rerun()
            
            cookbook_form(cookbook_db, edit_cookbook=edit_cookbook)
            return


    
    # with st.sidebar:
    #     page_more = sac_menu_buttons_func_other(items=['dashboard'])
    # if page == "Dashboard":
    #     cookbook_dashboard(meal_db)
    
    if page == "My Cookbooks":
        manage_cookbooks_page(meal_db, cookbook_db)
    
    elif page == "Browse Meals":
        filtered_meals = meal_search_sidebar(meal_db, cookbook_db)

        
        # display the images for each top meal as a small icon here
        st.markdown("<h1 style='text-align: center;'>🔪 Meals</h1>", unsafe_allow_html=True)
        display_meals_grid(filtered_meals, columns=2, meal_db=meal_db)
    
    elif page == "Add Meal":
        # Add tabs for different import methods
        tab1, tab2, tab3 = st.tabs(["📝 Manual Entry", "🌐 Import from URL", "📸 Extract from Image"])
        
        with tab1:
            meal_form(meal_db, cookbook_db=cookbook_db)
        
        with tab2:
            st.markdown("📝 Paste a recipe URL below and let AI extract the recipe information for you!")
            import_recipe_from_url(meal_db, cookbook_db)
        
        with tab3:
            st.markdown("📸 Take a photo of a recipe card or cookbook page to extract the text!")
            extract_recipe_from_image(meal_db, cookbook_db)

    print("User", st.session_state.get('username', 'guest'), "Cookbooks page load time:", (datetime.now() - s).total_seconds(), "seconds")
if __name__ == "__main__":
    main()

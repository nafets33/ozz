import streamlit as st
from master_cookbook.cookbook_db import MealDatabase, Meal, CookbookDatabase, Cookbook, save_meal_image
from master_cookbook.cookbook_utils import (
    display_meals_grid,
    meal_search_sidebar,
    meal_form,
    cookbook_dashboard,
    import_recipe_from_url,
    manage_cookbooks_page,
    view_cookbook_detail,
    cookbook_form
)
from master_ozz.utils import ozz_master_root
import os
import streamlit_antd_components as sac

def sac_menu_buttons_func():
    sac_menu_buttons = sac.buttons(
        items=['My Cookbooks', 'Browse Meals', 'Add Meal', 'Dashboard'],
        index=0,
        format_func='title',
        align='center',
        direction='horizontal',
        radius='lg',
        # compact=False,
        return_index=False,
    )

    return sac_menu_buttons

def main():    
    st.set_page_config(page_title="My Cookbook", layout="wide", page_icon="🍳")
    
    # Initialize databases
    meals_db_path = os.path.join(ozz_master_root(), "master_cookbook", "meals_db")
    cookbooks_db_path = os.path.join(ozz_master_root(), "master_cookbook", "cookbooks_db")
    
    meal_db = MealDatabase(meals_db_path)
    cookbook_db = CookbookDatabase(cookbooks_db_path)
    
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
    
    # Check if we're editing a meal
    if 'editing_meal_id' in st.session_state:
        meal_id = st.session_state['editing_meal_id']
        edit_meal = meal_db.get_meal(meal_id)
        
        if edit_meal:
            st.title(f"✏️ Edit Meal: {edit_meal.name}")
            
            if st.button("← Back to Browse"):
                del st.session_state['editing_meal_id']
                st.rerun()
            
            # Pass cookbook_db to meal_form
            meal_form(meal_db, edit_meal=edit_meal, cookbook_db=cookbook_db)
            return


    
    page = sac_menu_buttons_func()
    
    if page == "Dashboard":
        cookbook_dashboard(meal_db)
    
    elif page == "My Cookbooks":
        manage_cookbooks_page(meal_db, cookbook_db)
    
    elif page == "Browse Meals":
        st.title("🔍 Browse Meals")
        filtered_meals = meal_search_sidebar(meal_db, cookbook_db)
        display_meals_grid(filtered_meals, columns=2, meal_db=meal_db)
    
    elif page == "Add Meal":
        st.title("➕ Add New Meal")
        if st.toggle("Import from URL"):
            st.markdown("Paste a recipe URL below and let AI extract the recipe information for you!")
            import_recipe_from_url(meal_db, cookbook_db)
        else:
            # Pass cookbook_db to meal_form
            meal_form(meal_db, cookbook_db=cookbook_db)

if __name__ == "__main__":
    main()
import streamlit as st
from typing import List, Optional
import os
from master_cookbook.cookbook_db import Meal, MealDatabase, Cookbook, CookbookDatabase, save_meal_image, get_meal_image_path
from master_cookbook.cookbook_scraper import scrape_recipe_from_url
import requests

def display_cookbook_card(cookbook: Cookbook, meal_db: MealDatabase, cookbook_db: CookbookDatabase):
    """
    Display a single cookbook as a card.
    
    Args:
        cookbook: Cookbook object to display
        meal_db: MealDatabase instance
        cookbook_db: CookbookDatabase instance
    """
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(cookbook.name)
            st.caption(f"📚 {len(cookbook.meal_ids)} recipes")
            st.write(cookbook.description)
            
            # Display tags
            if cookbook.tags:
                tag_html = " ".join([f"<span style='background-color: #e0e0e0; padding: 2px 8px; border-radius: 10px; margin-right: 5px;'>{tag}</span>" for tag in cookbook.tags])
                st.markdown(tag_html, unsafe_allow_html=True)
        
        with col2:
            if st.button("📖 View", key=f"view_cookbook_{cookbook.cookbook_id}", use_container_width=True):
                st.session_state['viewing_cookbook_id'] = cookbook.cookbook_id
                st.rerun()
            
            if st.button("✏️ Edit", key=f"edit_cookbook_{cookbook.cookbook_id}", use_container_width=True):
                st.session_state['editing_cookbook_id'] = cookbook.cookbook_id
                st.rerun()
            if st.session_state.get('admin', False):
                if st.button("🗑️ Delete", key=f"delete_cookbook_{cookbook.cookbook_id}", use_container_width=True):
                    if cookbook_db.delete_cookbook(cookbook.cookbook_id):
                        st.success(f"Cookbook '{cookbook.name}' deleted!")
                        st.rerun()

        st.divider()


def cookbook_form(cookbook_db: CookbookDatabase, edit_cookbook: Optional[Cookbook] = None):
    """
    Display a form to create or edit a cookbook.
    
    Args:
        cookbook_db: CookbookDatabase instance
        edit_cookbook: Cookbook to edit (if None, creates new cookbook)
    """
    st.subheader("Create New Cookbook" if edit_cookbook is None else f"Edit: {edit_cookbook.name}")
    
    with st.form("cookbook_form"):
        name = st.text_input("Cookbook Name", value=edit_cookbook.name if edit_cookbook else "")
        description = st.text_area("Description", value=edit_cookbook.description if edit_cookbook else "", height=100)
        tags_text = st.text_input("Tags (comma separated)", 
                                   value=", ".join(edit_cookbook.tags) if edit_cookbook else "")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submitted = st.form_submit_button("💾 Save", use_container_width=True)
        with col2:
            if edit_cookbook:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
                if cancel:
                    if 'editing_cookbook_id' in st.session_state:
                        del st.session_state['editing_cookbook_id']
                    st.rerun()
    
    if submitted:
        tags = [t.strip() for t in tags_text.split(",") if t.strip()]
        
        if not name:
            st.error("Please provide a cookbook name")
            return
        
        if edit_cookbook:
            cookbook_db.update_cookbook(
                edit_cookbook.cookbook_id,
                name=name,
                description=description,
                tags=tags
            )
            st.success(f"✅ Cookbook '{name}' updated successfully!")
            if 'editing_cookbook_id' in st.session_state:
                del st.session_state['editing_cookbook_id']
        else:
            cookbook = Cookbook(
                name=name,
                description=description,
                tags=tags
            )
            cookbook_db.add_cookbook(cookbook)
            st.success(f"✅ Cookbook '{name}' created successfully!")
        
        st.rerun()


def view_cookbook_detail(cookbook: Cookbook, meal_db: MealDatabase, cookbook_db: CookbookDatabase):
    """
    Display detailed view of a cookbook with its meals.
    
    Args:
        cookbook: Cookbook to display
        meal_db: MealDatabase instance
        cookbook_db: CookbookDatabase instance
    """
    st.title(f"📖 {cookbook.name}")
    
    if st.button("← Back to Cookbooks"):
        del st.session_state['viewing_cookbook_id']
        st.rerun()
    
    st.write(cookbook.description)
    
    if cookbook.tags:
        tag_html = " ".join([f"<span style='background-color: #e0e0e0; padding: 2px 8px; border-radius: 10px; margin-right: 5px;'>{tag}</span>" for tag in cookbook.tags])
        st.markdown(tag_html, unsafe_allow_html=True)
    
    st.divider()
    
    # Add meals section with MULTI-SELECT
    st.subheader("➕ Add Meals to This Cookbook")
    
    all_meals = meal_db.get_all_meals()
    available_meals = [m for m in all_meals if m.meal_id not in cookbook.meal_ids]
    
    if available_meals:
        # Create a multiselect with meal names
        meal_options = {f"{m.name} ({m.category})": m for m in available_meals}
        
        selected_meal_names = st.multiselect(
            "Select meals to add:",
            options=list(meal_options.keys()),
            help="You can select multiple meals to add at once"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("➕ Add Selected Meals", disabled=len(selected_meal_names) == 0):
                # Add all selected meals
                added_count = 0
                for meal_name in selected_meal_names:
                    meal = meal_options[meal_name]
                    if cookbook_db.add_meal_to_cookbook(cookbook.cookbook_id, meal.meal_id):
                        added_count += 1
                
                if added_count > 0:
                    st.success(f"✅ Added {added_count} meal(s) to cookbook!")
                    st.rerun()
        
        with col2:
            st.caption(f"Selected: {len(selected_meal_names)} meal(s)")
    else:
        st.info("All meals are already in this cookbook!")
    
    st.divider()
    
    # Display meals in cookbook
    st.subheader(f"📚 Recipes in This Cookbook")
    
    if cookbook.meal_ids:
        # Get all meals - Filter out invalid IDs
        meals_in_cookbook = []
        invalid_meal_ids = []
        
        for meal_id in cookbook.meal_ids:
            meal = meal_db.get_meal(meal_id)
            if meal:
                meals_in_cookbook.append(meal)
            else:
                invalid_meal_ids.append(meal_id)
        
        # Clean up invalid meal IDs from cookbook
        if invalid_meal_ids:
            st.warning(f"⚠️ Found {len(invalid_meal_ids)} invalid meal reference(s). Click to clean up:")
            if st.button("🧹 Remove Invalid References"):
                for invalid_id in invalid_meal_ids:
                    cookbook_db.remove_meal_from_cookbook(cookbook.cookbook_id, invalid_id)
                st.success("Cleaned up invalid references!")
                st.rerun()
        
        if not meals_in_cookbook:
            st.info("No valid meals in this cookbook. Add some above!")
            return
        
        st.write(f"**Showing {len(meals_in_cookbook)} recipe(s)**")
        
        # Option to remove multiple meals at once
        if len(meals_in_cookbook) > 1:
            if st.button("🗑️ Remove Multiple Meals"):
                st.session_state['removing_multiple'] = True
                st.rerun()
        
        if st.session_state.get('removing_multiple', False):
            st.write("**Select meals to remove:**")
            
            meals_to_remove = []
            for meal in meals_in_cookbook:
                if st.checkbox(f"{meal.name} ({meal.category})", key=f"remove_check_{meal.meal_id}"):
                    meals_to_remove.append(meal)
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("✅ Remove Selected", disabled=len(meals_to_remove) == 0):
                    removed_count = 0
                    for meal in meals_to_remove:
                        if cookbook_db.remove_meal_from_cookbook(cookbook.cookbook_id, meal.meal_id):
                            removed_count += 1
                    
                    if removed_count > 0:
                        st.success(f"Removed {removed_count} meal(s)!")
                        st.session_state['removing_multiple'] = False
                        st.rerun()
            
            with col2:
                if st.button("❌ Cancel"):
                    st.session_state['removing_multiple'] = False
                    st.rerun()
            
            st.divider()
        
        # Display each meal as a proper card
        for idx, meal in enumerate(meals_in_cookbook):
            with st.container():
                # Create a two-column layout: image on left, details on right
                col_img, col_details = st.columns([1, 3])
                
                with col_img:
                    # Show meal image
                    image_path = meal.get_image_path()
                    if image_path and os.path.exists(image_path):
                        st.image(image_path, use_container_width=True)
                    else:
                        st.info("No image")
                
                with col_details:
                    # Meal title and category
                    st.markdown(f"### {meal.name}")
                    st.caption(f"Category: {meal.category.title()}")
                    
                    # Show brief info
                    info_parts = []
                    if meal.prep_time_minutes:
                        info_parts.append(f"⏱️ {meal.prep_time_minutes} min")
                    if meal.servings:
                        info_parts.append(f"🍽️ {meal.servings} servings")
                    if meal.calories:
                        info_parts.append(f"🔥 {meal.calories} cal")
                    
                    if info_parts:
                        st.caption(" | ".join(info_parts))
                    
                    # Description
                    if meal.description:
                        st.write(meal.description)
                    
                    # Tags
                    if meal.other_tags:
                        tag_html = " ".join([f"<span style='background-color: #e0e0e0; padding: 2px 8px; border-radius: 10px; margin-right: 5px;'>{tag}</span>" for tag in meal.other_tags])
                        st.markdown(tag_html, unsafe_allow_html=True)
                    
                    # Show ingredients in expander
                    with st.expander("📝 View Ingredients & Instructions"):
                        st.write("**Ingredients:**")
                        for ingredient in meal.ingredients:
                            st.write(f"- {ingredient}")
                        
                        if meal.prep_instructions:
                            st.write("**Instructions:**")
                            st.write(meal.prep_instructions)
                    
                    # Action buttons (only show if not in multi-remove mode)
                    if not st.session_state.get('removing_multiple', False):
                        col_btn1, col_btn2, col_btn3 = st.columns([1.5, 1.5, 5])
                        
                        with col_btn1:
                            if st.button("✏️ Edit", key=f"edit_meal_{meal.meal_id}", use_container_width=True):
                                st.session_state['editing_meal_id'] = meal.meal_id
                                st.rerun()
                        
                        with col_btn2:
                            if st.button("🗑️ Remove", key=f"remove_{meal.meal_id}", use_container_width=True, help="Remove from cookbook"):
                                if cookbook_db.remove_meal_from_cookbook(cookbook.cookbook_id, meal.meal_id):
                                    st.success(f"Removed '{meal.name}' from cookbook!")
                                    st.rerun()
                
                st.divider()
    else:
        st.info("No recipes in this cookbook yet. Add some above!")


def manage_cookbooks_page(meal_db: MealDatabase, cookbook_db: CookbookDatabase):
    """
    Main page for managing cookbooks.
    
    Args:
        meal_db: MealDatabase instance
        cookbook_db: CookbookDatabase instance
    """
    st.title("📚 My Cookbooks")
    
    # Check if we're in create mode
    if st.session_state.get('creating_cookbook', False):
        st.subheader("➕ Create New Cookbook")
        cookbook_form(cookbook_db)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("❌ Cancel Create"):
                st.session_state['creating_cookbook'] = False
                st.rerun()
        
        st.divider()
        st.write("---")
        st.subheader("Existing Cookbooks")
    
    # Show create button (only if not already creating)
    if not st.session_state.get('creating_cookbook', False):
        if st.button("➕ Create New Cookbook"):
            st.session_state['creating_cookbook'] = True
            st.rerun()
        
        st.divider()
    
    # Display all cookbooks (ALWAYS show this section)
    cookbooks = cookbook_db.get_all_cookbooks()
    
    if not cookbooks:
        st.info("No cookbooks yet. Create your first cookbook above!")
        return
    
    st.write(f"**Total Cookbooks: {len(cookbooks)}**")
    st.divider()
    
    for cookbook in cookbooks:
        display_cookbook_card(cookbook, meal_db, cookbook_db)


def display_meal_card(meal: Meal, show_full_details: bool = False, meal_db: Optional[MealDatabase] = None):
    """
    Display a single meal as a card in Streamlit.
    
    Args:
        meal: Meal object to display
        show_full_details: If True, shows full details including prep instructions
        meal_db: MealDatabase instance (needed for edit/delete operations)
    """
    with st.container():
        # Image
        image_path = meal.get_image_path()
        if image_path and os.path.exists(image_path):
            st.image(image_path, width=200)
        else:
            st.info("No image available")
        
        # Meal name and category
        st.subheader(meal.name)
        st.caption(f"Category: {meal.category.title()}")
        
        # Display tags
        if meal.other_tags:
            tag_html = " ".join([f"<span style='background-color: #e0e0e0; padding: 2px 8px; border-radius: 10px; margin-right: 5px;'>{tag}</span>" for tag in meal.other_tags])
            st.markdown(tag_html, unsafe_allow_html=True)
        
        # Meal info - display inline without nested columns
        info_parts = []
        if meal.prep_time_minutes:
            info_parts.append(f"⏱️ {meal.prep_time_minutes} min")
        if meal.servings:
            info_parts.append(f"🍽️ {meal.servings} servings")
        if meal.calories:
            info_parts.append(f"🔥 {meal.calories} cal")
        
        if info_parts:
            st.markdown(" | ".join(info_parts))
        
        # Description
        st.write(meal.description)
        
        # Full details expander
        if show_full_details:
            with st.expander("View Full Details"):
                st.write("**Ingredients:**")
                for ingredient in meal.ingredients:
                    st.write(f"- {ingredient}")
                
                st.write("**Preparation Instructions:**")
                st.write(meal.prep_instructions)
        
        # Edit and Delete buttons (only if meal_db is provided)
        if meal_db is not None:
            # Check if we're in delete confirmation mode for this meal
            delete_confirm_key = f'delete_confirm_{meal.meal_id}'
            
            if st.session_state.get(delete_confirm_key, False):
                # Show confirmation buttons
                st.warning(f"⚠️ Are you sure you want to delete '{meal.name}'?")
                col1, col2, col3 = st.columns([1.5, 1.5, 5])
                
                with col1:
                    if st.button("✅ Confirm", key=f"confirm_delete_{meal.meal_id}", use_container_width=True):
                        if meal_db.delete_meal(meal.meal_id):
                            st.success(f"Meal '{meal.name}' deleted!")
                            # Clean up session state
                            if delete_confirm_key in st.session_state:
                                del st.session_state[delete_confirm_key]
                        else:
                            st.error("Failed to delete meal")
                            if delete_confirm_key in st.session_state:
                                del st.session_state[delete_confirm_key]
                
                with col2:
                    if st.button("❌ Cancel", key=f"cancel_delete_{meal.meal_id}", use_container_width=True):
                        # Clean up session state
                        if delete_confirm_key in st.session_state:
                            del st.session_state[delete_confirm_key]
                        st.rerun()
            else:
                # Show normal edit/delete buttons
                col1, col2, col3 = st.columns([1.5, 1.5, 5])
                with col1:
                    if st.button("✏️ Edit", key=f"edit_{meal.meal_id}", use_container_width=True):
                        st.session_state['editing_meal_id'] = meal.meal_id
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{meal.meal_id}", use_container_width=True):
                        # Set confirmation mode
                        st.session_state[delete_confirm_key] = True
                        st.rerun()
        
        st.divider()


def display_meals_grid(meals: List[Meal], columns: int = 2, meal_db: Optional[MealDatabase] = None):
    """
    Display meals in a grid layout.
    
    Args:
        meals: List of Meal objects
        columns: Number of columns in the grid
        meal_db: MealDatabase instance (for edit/delete operations)
    """
    if not meals:
        st.warning("No meals to display")
        return
    
    # Create rows of columns
    for i in range(0, len(meals), columns):
        cols = st.columns(columns)
        for j, col in enumerate(cols):
            meal_index = i + j
            if meal_index < len(meals):
                with col:
                    display_meal_card(meals[meal_index], show_full_details=True, meal_db=meal_db)


def meal_search_sidebar(meal_db: MealDatabase, cookbook_db: Optional[CookbookDatabase] = None) -> List[Meal]:
    """
    Create a sidebar with search and filter options.
    
    Args:
        meal_db: MealDatabase instance
        cookbook_db: CookbookDatabase instance (optional, for cookbook filtering)
    
    Returns:
        List of filtered meals
    """
    with st.expander("🔍 Search & Filter Options", expanded=False):
    
        # Category filter
        categories = ['all'] + sorted(set(meal.category for meal in meal_db.get_all_meals()))
        selected_category = st.selectbox("Category", categories)

        # Search by name
        search_name = st.text_input("Search by name")

        # Search by ingredient
        search_ingredient = st.text_input("Search by ingredient")
        
        # Tag filter
        all_tags = sorted(set(tag for meal in meal_db.get_all_meals() for tag in meal.other_tags))
        if all_tags:
            selected_tags = st.multiselect("Filter by tags", all_tags)
        else:
            selected_tags = []
        
        # Cookbook filter (if cookbook_db is provided)
        selected_cookbook_id = None
        if cookbook_db is not None:
            all_cookbooks = cookbook_db.get_all_cookbooks()
            if all_cookbooks:
                cookbook_options = {cb.name: cb.cookbook_id for cb in all_cookbooks}
                cookbook_options['All Cookbooks'] = None
                
                selected_cookbook_name = st.selectbox(
                    "Filter by cookbook",
                    options=['All Cookbooks'] + list(cookbook_options.keys())[:-1],  # Exclude the 'All Cookbooks' we just added
                    help="Show only meals in a specific cookbook"
                )
                
                if selected_cookbook_name != 'All Cookbooks':
                    selected_cookbook_id = cookbook_options[selected_cookbook_name]
    
    # Apply filters
    meals = meal_db.get_all_meals()
    
    # Filter by cookbook first (if selected)
    if selected_cookbook_id is not None and cookbook_db is not None:
        cookbook = cookbook_db.get_cookbook(selected_cookbook_id)
        if cookbook:
            meals = [m for m in meals if m.meal_id in cookbook.meal_ids]
    
    if selected_category != 'all':
        meals = [m for m in meals if m.category == selected_category]
    
    if search_name:
        meals = [m for m in meals if search_name.lower() in m.name.lower()]
    
    if search_ingredient:
        meals = [m for m in meals if any(search_ingredient.lower() in ing.lower() for ing in m.ingredients)]
    
    if selected_tags:
        meals = [m for m in meals if any(tag in m.other_tags for tag in selected_tags)]
    
    return meals


def meal_form(meal_db: MealDatabase, edit_meal: Optional[Meal] = None, cookbook_db: Optional[CookbookDatabase] = None, scraped_data: Optional[dict] = None):
    """
    Display a form to create or edit a meal.
    
    Args:
        meal_db: MealDatabase instance
        edit_meal: Meal to edit (if None, creates new meal)
        cookbook_db: CookbookDatabase instance (optional, for cookbook assignment)
        scraped_data: Dictionary with scraped recipe data and image_url (optional)
    """
    
    # Detect if this is a scraped import
    is_scraped = scraped_data is not None
    
    if is_scraped:
        st.subheader("📥 Import Recipe from URL")
        st.info(f"📌 Source: {scraped_data.get('source_domain', 'Unknown')}")
    else:
        st.subheader("Add New Meal" if edit_meal is None else f"Edit: {edit_meal.name}")
    
    # Image upload FIRST (outside form)
    st.write("**Meal Image:**")
    
    # Show current image if editing
    current_image_filename = edit_meal.image_filename if edit_meal else None
    
    if current_image_filename:
        current_image_path = edit_meal.get_image_path()
        if current_image_path and os.path.exists(current_image_path):
            st.image(current_image_path, caption="Current Image", width=300)
            if st.button("🗑️ Delete Current Image"):
                edit_meal.delete_image()
                current_image_filename = None
                st.success("Image deleted!")
                st.rerun()
    
    # Handle scraped image URL
    if is_scraped and scraped_data.get('image_url') and not current_image_filename:
        col1, col2 = st.columns([1, 2])
        with col1:
            try:
                st.image(scraped_data['image_url'], caption="Scraped Image", width=300)
                if st.button("📥 Download & Use This Image"):
                    with st.spinner("Downloading image..."):
                        try:
                            response = requests.get(scraped_data['image_url'], timeout=10)
                            if response.status_code == 200:
                                # Create a temporary file-like object
                                class UploadedFile:
                                    def __init__(self, content, name):
                                        self.content = content
                                        self.name = name
                                    def getbuffer(self):
                                        return self.content
                                
                                file_ext = scraped_data['image_url'].split('.')[-1].split('?')[0]
                                if file_ext not in ['jpg', 'jpeg', 'png', 'gif']:
                                    file_ext = 'jpg'
                                
                                temp_file = UploadedFile(response.content, f"temp.{file_ext}")
                                current_image_filename = save_meal_image(
                                    temp_file,
                                    scraped_data.get('name', 'recipe'),
                                    scraped_data.get('category', 'lunch')
                                )
                                st.session_state['downloaded_image'] = current_image_filename
                                st.success("✅ Image downloaded!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error downloading image: {e}")
            except Exception as e:
                st.warning(f"Could not load image: {e}")
        
        st.divider()
    
    # Check if we downloaded an image in this session
    if st.session_state.get('downloaded_image'):
        current_image_filename = st.session_state['downloaded_image']
        st.success(f"✅ Using downloaded image")
    
    uploaded_file = st.file_uploader(
        "Upload new image" if current_image_filename else "Choose an image",
        type=['png', 'jpg', 'jpeg', 'gif'],
        key=f"image_uploader_{edit_meal.meal_id if edit_meal else 'new'}"
    )
    
    # Preview uploaded image
    if uploaded_file is not None:
        st.image(uploaded_file, caption="New Image Preview", width=300)
    
    st.divider()
    
    # Cookbook assignment (if cookbook_db is provided)
    selected_cookbook_ids = []
    if cookbook_db is not None:
        st.write("**📚 Assign to Cookbooks:**")
        
        all_cookbooks = cookbook_db.get_all_cookbooks()
        
        if all_cookbooks:
            # Get current cookbooks for this meal
            current_cookbooks = []
            if edit_meal and edit_meal.meal_id:
                current_cookbooks = [cb.cookbook_id for cb in cookbook_db.get_cookbooks_for_meal(edit_meal.meal_id)]
            
            # Create multiselect for cookbooks
            cookbook_options = {cb.name: cb.cookbook_id for cb in all_cookbooks}
            
            # Pre-select current cookbooks
            default_selections = [name for name, cb_id in cookbook_options.items() if cb_id in current_cookbooks]
            
            selected_cookbook_names = st.multiselect(
                "Add this meal to cookbooks:",
                options=list(cookbook_options.keys()),
                default=default_selections,
                help="You can add this meal to multiple cookbooks"
            )
            
            selected_cookbook_ids = [cookbook_options[name] for name in selected_cookbook_names]
            
            st.caption(f"This meal will be in {len(selected_cookbook_ids)} cookbook(s)")
        else:
            st.info("No cookbooks created yet. Create a cookbook first to organize your meals!")
        
        st.divider()
    
    # Get default values (either from edit_meal or scraped_data)
    default_name = ""
    default_category = "lunch"
    default_description = ""
    default_ingredients = []
    default_prep_instructions = ""
    default_prep_time = 0
    default_servings = 1
    default_calories = 0
    default_tags = []
    
    if edit_meal:
        default_name = edit_meal.name
        default_category = edit_meal.category
        default_description = edit_meal.description
        default_ingredients = edit_meal.ingredients
        default_prep_instructions = edit_meal.prep_instructions
        default_prep_time = edit_meal.prep_time_minutes or 0
        default_servings = edit_meal.servings or 1
        default_calories = edit_meal.calories or 0
        default_tags = edit_meal.other_tags
    elif scraped_data:
        default_name = scraped_data.get('name', '')
        default_category = scraped_data.get('category', 'lunch')
        default_description = scraped_data.get('description', '')
        default_ingredients = scraped_data.get('ingredients', [])
        default_prep_instructions = scraped_data.get('prep_instructions', '')
        default_prep_time = int(scraped_data.get('prep_time_minutes', 0) or 0)
        default_servings = int(scraped_data.get('servings', 1) or 1)
        default_calories = int(scraped_data.get('calories', 0) or 0)
        default_tags = scraped_data.get('other_tags', [])
        # Add source domain tag
        if scraped_data.get('source_domain'):
            default_tags.append(f"from-{scraped_data['source_domain']}")
    
    # Form for meal details
    with st.form("meal_form"):
        # Basic info
        name = st.text_input("Meal Name", value=default_name)
        category = st.selectbox("Category", ['breakfast', 'lunch', 'dinner', 'snack', 'dessert'], 
                                index=['breakfast', 'lunch', 'dinner', 'snack', 'dessert'].index(default_category))
        
        # Meal details
        st.write("**Nutritional Information:**")
        cols = st.columns(3)
        prep_time = cols[0].number_input("Prep Time (min)", min_value=0, value=default_prep_time)
        servings = cols[1].number_input("Servings", min_value=1, value=default_servings)
        calories = cols[2].number_input("Calories", min_value=0, value=default_calories)
        
        # Description and instructions
        description = st.text_area("Description", value=default_description, height=100)
        prep_instructions = st.text_area("Preparation Instructions", value=default_prep_instructions, height=200)
        
        # Ingredients (one per line)
        ingredients_text = st.text_area("Ingredients (one per line)", 
                                        value="\n".join(default_ingredients), 
                                        height=150)
        
        # Tags (comma separated)
        tags_text = st.text_input("Tags (comma separated)", 
                                   value=", ".join(default_tags))
        
        # Submit buttons
        col1, col2 = st.columns([1, 4])
        with col1:
            submitted = st.form_submit_button("💾 Save Meal", use_container_width=True)
        with col2:
            if edit_meal or is_scraped:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
                if cancel:
                    if 'editing_meal_id' in st.session_state:
                        del st.session_state['editing_meal_id']
                    if 'scraped_recipe' in st.session_state:
                        del st.session_state['scraped_recipe']
                    if 'downloaded_image' in st.session_state:
                        del st.session_state['downloaded_image']
                    st.rerun()
    
    if submitted:
        # Parse ingredients and tags
        ingredients = [i.strip() for i in ingredients_text.split("\n") if i.strip()]
        tags = [t.strip() for t in tags_text.split(",") if t.strip()]
        
        if not name or not ingredients:
            st.error("Please provide at least a name and ingredients")
            return
        
        # Handle image upload
        image_filename = current_image_filename  # Keep existing image by default
        
        if uploaded_file is not None:
            try:
                # Delete old image if replacing
                if edit_meal and edit_meal.meal_id and edit_meal.image_filename:
                    edit_meal.delete_image()
                
                image_filename = save_meal_image(uploaded_file, name, category)
                st.success("Image uploaded successfully!")
            except Exception as e:
                st.error(f"Error uploading image: {e}")
        
        if edit_meal and edit_meal.meal_id:
            # Update existing meal
            meal_db.update_meal(
                edit_meal.meal_id,
                name=name,
                category=category,
                ingredients=ingredients,
                description=description,
                prep_instructions=prep_instructions,
                image_filename=image_filename,
                other_tags=tags,
                prep_time_minutes=prep_time if prep_time > 0 else None,
                servings=servings if servings > 0 else None,
                calories=calories if calories > 0 else None
            )
            meal_id = edit_meal.meal_id
            st.success(f"✅ Meal '{name}' updated successfully!")
            
        else:
            # Create new meal (either manual or scraped)
            meal = Meal(
                name=name,
                category=category,
                ingredients=ingredients,
                description=description,
                prep_instructions=prep_instructions,
                image_filename=image_filename,
                other_tags=tags,
                prep_time_minutes=prep_time if prep_time > 0 else None,
                servings=servings if servings > 0 else None,
                calories=calories if calories > 0 else None
            )
            meal_db.add_meal(meal)
            meal_id = meal.meal_id
            
            if is_scraped:
                st.success(f"✅ Recipe '{name}' imported successfully!")
            else:
                st.success(f"✅ Meal '{name}' added successfully!")
        
        # Handle cookbook assignments
        if cookbook_db is not None:
            # Get current cookbooks for this meal
            current_cookbooks = cookbook_db.get_cookbooks_for_meal(meal_id)
            current_cookbook_ids = [cb.cookbook_id for cb in current_cookbooks]
            
            # Add to new cookbooks
            for cookbook_id in selected_cookbook_ids:
                if cookbook_id not in current_cookbook_ids:
                    cookbook_db.add_meal_to_cookbook(cookbook_id, meal_id)
            
            # Remove from unchecked cookbooks
            for cookbook_id in current_cookbook_ids:
                if cookbook_id not in selected_cookbook_ids:
                    cookbook_db.remove_meal_from_cookbook(cookbook_id, meal_id)
            
            st.success(f"📚 Cookbook assignments updated!")
        
        # Clear all session states
        if 'editing_meal_id' in st.session_state:
            del st.session_state['editing_meal_id']
        if 'scraped_recipe' in st.session_state:
            del st.session_state['scraped_recipe']
        if 'downloaded_image' in st.session_state:
            del st.session_state['downloaded_image']
        
        st.rerun()


def import_recipe_from_url(meal_db: MealDatabase, cookbook_db: Optional[CookbookDatabase] = None):
    """
    Display a form to import a recipe from a URL.
    
    Args:
        meal_db: MealDatabase instance
        cookbook_db: CookbookDatabase instance (optional, for cookbook assignment)
    """
    st.subheader("Import Recipe from URL")
    
    url = st.text_input("Enter Recipe URL", placeholder="https://example.com/recipe")
    
    if st.button("Scrape Recipe"):
        if not url:
            st.error("Please enter a URL")
            return
        
        with st.spinner("Scraping recipe..."):
            recipe_data = scrape_recipe_from_url(url)
        
        if not recipe_data:
            st.error("Failed to scrape recipe. The website might not be supported or the URL is invalid.")
            return
        
        # Store in session state
        st.session_state['scraped_recipe'] = recipe_data
        st.success("Recipe scraped successfully! Review and edit before saving:")
        st.rerun()
    
    # Show form if we have scraped data
    if 'scraped_recipe' in st.session_state:
        scraped_data = st.session_state['scraped_recipe']
        
        # Add cancel button
        if st.button("❌ Cancel Import"):
            if 'scraped_recipe' in st.session_state:
                del st.session_state['scraped_recipe']
            if 'downloaded_image' in st.session_state:
                del st.session_state['downloaded_image']
            st.rerun()
        
        st.divider()
        
        # Use meal_form with scraped_data parameter
        meal_form(meal_db, edit_meal=None, cookbook_db=cookbook_db, scraped_data=scraped_data)
                

def cookbook_dashboard(meal_db: MealDatabase):
    """
    Display a dashboard with meal statistics and overview.
    
    Args:
        meal_db: MealDatabase instance
    """
    st.header("Cookbook Dashboard")
    
    # Stats
    cols = st.columns(4)
    cols[0].metric("Total Meals", meal_db.get_meal_count())
    
    category_summary = meal_db.get_categories_summary()
    cols[1].metric("Breakfast", category_summary.get('breakfast', 0))
    cols[2].metric("Lunch", category_summary.get('lunch', 0))
    cols[3].metric("Dinner", category_summary.get('dinner', 0))
    
    # Category breakdown chart
    if category_summary:
        st.subheader("Meals by Category")
        st.bar_chart(category_summary)
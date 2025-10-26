import os
import json
from typing import List, Optional, Dict
from datetime import datetime
from dataclasses import dataclass, asdict, field

# Utility functions for managing meal images
def get_cookbook_images_dir() -> str:
    """Get the directory for storing cookbook images."""
    from master_ozz.utils import ozz_master_root
    images_dir = os.path.join(ozz_master_root(), "master_cookbook", "images")
    os.makedirs(images_dir, exist_ok=True)
    return images_dir


def save_meal_image(uploaded_file, meal_name: str, category: str) -> str:
    """
    Save uploaded image with unique ID based on meal name and category.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        meal_name: Name of the meal
        category: Category of the meal
        
    Returns:
        Filename of saved image
    """
    images_dir = get_cookbook_images_dir()
    
    # Create unique filename: name_category_timestamp.extension
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name_slug = meal_name.lower().replace(" ", "_").replace("/", "_")
    category_slug = category.lower()
    
    # Get file extension
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    # Create filename
    filename = f"{name_slug}_{category_slug}_{timestamp}.{file_ext}"
    filepath = os.path.join(images_dir, filename)
    
    # Save the file
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return filename


def get_meal_image_path(image_filename: str) -> str:
    """
    Get the full path to a meal image.
    
    Args:
        image_filename: Filename of the image
        
    Returns:
        Full path to the image
    """
    if not image_filename:
        return None
    
    images_dir = get_cookbook_images_dir()
    return os.path.join(images_dir, image_filename)


def delete_meal_image(image_filename: str) -> bool:
    """
    Delete a meal image file.
    
    Args:
        image_filename: Filename of the image to delete
        
    Returns:
        True if deleted successfully, False otherwise
    """
    if not image_filename:
        return False
    
    try:
        filepath = get_meal_image_path(image_filename)
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        print(f"Error deleting image: {e}")
    
    return False

# Utility functions for managing meal images #


@dataclass
class Meal:
    """
    A class to represent a meal with all its details.
    """
    name: str
    category: str  # breakfast, lunch, dinner
    ingredients: List[str]
    description: str
    prep_instructions: str
    image_filename: Optional[str] = None  # Changed from image_path to image_filename
    other_tags: List[str] = field(default_factory=list)
    prep_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    calories: Optional[int] = None
    created_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    meal_id: Optional[str] = None

    # ...existing __post_init__, _generate_meal_id, to_dict, to_json, from_dict, from_json methods...
    
    def get_image_path(self) -> Optional[str]:
        """Get the full path to the meal's image."""
        return get_meal_image_path(self.image_filename)
    
    def delete_image(self) -> bool:
        """Delete the meal's image file."""
        return delete_meal_image(self.image_filename)


    def __post_init__(self):
        """Validate and set defaults after initialization."""
        # Validate category
        valid_categories = ['breakfast', 'lunch', 'dinner', 'snack', 'dessert']
        if self.category.lower() not in valid_categories:
            raise ValueError(f"Category must be one of {valid_categories}")
        
        self.category = self.category.lower()
        
        # Generate meal_id if not provided
        if not self.meal_id:
            self.meal_id = self._generate_meal_id()

    def _generate_meal_id(self) -> str:
        """Generate a unique meal ID based on name and timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        name_slug = self.name.lower().replace(" ", "_")
        return f"{name_slug}_{timestamp}"

    def to_dict(self) -> Dict:
        """Convert meal to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert meal to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Meal':
        """Create a Meal instance from a dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'Meal':
        """Create a Meal instance from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def save_to_file(self, filepath: str):
        """Save meal to a JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, filepath: str) -> 'Meal':
        """Load meal from a JSON file."""
        with open(filepath, 'r') as f:
            return cls.from_json(f.read())

    def update(self, **kwargs):
        """Update meal attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def add_tag(self, tag: str):
        """Add a tag to other_tags."""
        if tag not in self.other_tags:
            self.other_tags.append(tag)

    def remove_tag(self, tag: str):
        """Remove a tag from other_tags."""
        if tag in self.other_tags:
            self.other_tags.remove(tag)

    def __str__(self) -> str:
        """String representation of the meal."""
        return f"{self.name} ({self.category}) - {len(self.ingredients)} ingredients"


class MealDatabase:
    """
    A class to manage a collection of meals.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.meals: Dict[str, Meal] = {}
        self._load_database()

    def _load_database(self):
        """Load all meals from the database directory."""
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path, exist_ok=True)
            return

        for filename in os.listdir(self.db_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.db_path, filename)
                try:
                    meal = Meal.load_from_file(filepath)
                    self.meals[meal.meal_id] = meal
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

    def add_meal(self, meal: Meal) -> str:
        """Add a meal to the database."""
        self.meals[meal.meal_id] = meal
        filepath = os.path.join(self.db_path, f"{meal.meal_id}.json")
        meal.save_to_file(filepath)
        return meal.meal_id

    def get_meal(self, meal_id: str) -> Optional[Meal]:
        """Get a meal by ID."""
        return self.meals.get(meal_id)

    def delete_meal(self, meal_id: str) -> bool:
        """Delete a meal from the database."""
        if meal_id in self.meals:
            filepath = os.path.join(self.db_path, f"{meal_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            del self.meals[meal_id]
            return True
        return False

    def update_meal(self, meal_id: str, **kwargs) -> bool:
        """Update a meal in the database."""
        meal = self.get_meal(meal_id)
        if meal:
            meal.update(**kwargs)
            filepath = os.path.join(self.db_path, f"{meal_id}.json")
            meal.save_to_file(filepath)
            return True
        return False

    def search_by_category(self, category: str) -> List[Meal]:
        """Search meals by category."""
        return [meal for meal in self.meals.values() if meal.category == category.lower()]

    def search_by_tag(self, tag: str) -> List[Meal]:
        """Search meals by tag."""
        return [meal for meal in self.meals.values() if tag.lower() in [t.lower() for t in meal.other_tags]]

    def search_by_ingredient(self, ingredient: str) -> List[Meal]:
        """Search meals by ingredient."""
        ingredient_lower = ingredient.lower()
        return [
            meal for meal in self.meals.values() 
            if any(ingredient_lower in ing.lower() for ing in meal.ingredients)
        ]

    def search_by_name(self, name: str) -> List[Meal]:
        """Search meals by name (partial match)."""
        name_lower = name.lower()
        return [meal for meal in self.meals.values() if name_lower in meal.name.lower()]

    def get_all_meals(self) -> List[Meal]:
        """Get all meals."""
        return list(self.meals.values())

    def get_meal_count(self) -> int:
        """Get total number of meals."""
        return len(self.meals)

    def get_categories_summary(self) -> Dict[str, int]:
        """Get count of meals per category."""
        summary = {}
        for meal in self.meals.values():
            summary[meal.category] = summary.get(meal.category, 0) + 1
        return summary


@dataclass
class Cookbook:
    """
    A class to represent a cookbook that contains multiple meals.
    """
    name: str
    description: str
    meal_ids: List[str] = field(default_factory=list)
    created_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    cookbook_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.cookbook_id is None:
            self.cookbook_id = self._generate_cookbook_id()
    
    def _generate_cookbook_id(self) -> str:
        """Generate a unique ID for the cookbook."""
        import hashlib
        unique_string = f"{self.name}_{self.created_date}_{datetime.now().timestamp()}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def add_meal(self, meal_id: str):
        """Add a meal to this cookbook."""
        if meal_id not in self.meal_ids:
            self.meal_ids.append(meal_id)
    
    def remove_meal(self, meal_id: str):
        """Remove a meal from this cookbook."""
        if meal_id in self.meal_ids:
            self.meal_ids.remove(meal_id)
    
    def to_dict(self) -> dict:
        """Convert cookbook to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert cookbook to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Cookbook':
        """Create Cookbook from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Cookbook':
        """Create Cookbook from JSON string."""
        return cls.from_dict(json.loads(json_str))


class CookbookDatabase:
    """
    A class to manage multiple cookbooks.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)
        self.cookbooks: Dict[str, Cookbook] = {}
        self.load_all_cookbooks()
    
    def load_all_cookbooks(self):
        """Load all cookbooks from the database directory."""
        for filename in os.listdir(self.db_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.db_path, filename)
                try:
                    with open(filepath, 'r') as f:
                        cookbook = Cookbook.from_json(f.read())
                        self.cookbooks[cookbook.cookbook_id] = cookbook
                except Exception as e:
                    print(f"Error loading cookbook {filename}: {e}")
    
    def add_cookbook(self, cookbook: Cookbook) -> bool:
        """Add a new cookbook to the database."""
        try:
            self.cookbooks[cookbook.cookbook_id] = cookbook
            self._save_cookbook(cookbook)
            return True
        except Exception as e:
            print(f"Error adding cookbook: {e}")
            return False
    
    def _save_cookbook(self, cookbook: Cookbook):
        """Save a cookbook to disk."""
        filepath = os.path.join(self.db_path, f"{cookbook.cookbook_id}.json")
        with open(filepath, 'w') as f:
            f.write(cookbook.to_json())
    
    def get_cookbook(self, cookbook_id: str) -> Optional[Cookbook]:
        """Get a cookbook by ID."""
        return self.cookbooks.get(cookbook_id)
    
    def get_all_cookbooks(self) -> List[Cookbook]:
        """Get all cookbooks."""
        return list(self.cookbooks.values())
    
    def update_cookbook(self, cookbook_id: str, **kwargs) -> bool:
        """Update a cookbook's fields."""
        if cookbook_id in self.cookbooks:
            cookbook = self.cookbooks[cookbook_id]
            for key, value in kwargs.items():
                if hasattr(cookbook, key):
                    setattr(cookbook, key, value)
            self._save_cookbook(cookbook)
            return True
        return False
    
    def delete_cookbook(self, cookbook_id: str) -> bool:
        """Delete a cookbook."""
        if cookbook_id in self.cookbooks:
            filepath = os.path.join(self.db_path, f"{cookbook_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            del self.cookbooks[cookbook_id]
            return True
        return False
    
    def add_meal_to_cookbook(self, cookbook_id: str, meal_id: str) -> bool:
        """Add a meal to a cookbook."""
        cookbook = self.get_cookbook(cookbook_id)
        if cookbook:
            cookbook.add_meal(meal_id)
            self._save_cookbook(cookbook)
            return True
        return False
    
    def remove_meal_from_cookbook(self, cookbook_id: str, meal_id: str) -> bool:
        """Remove a meal from a cookbook."""
        cookbook = self.get_cookbook(cookbook_id)
        if cookbook:
            cookbook.remove_meal(meal_id)
            self._save_cookbook(cookbook)
            return True
        return False
    
    def get_cookbooks_for_meal(self, meal_id: str) -> List[Cookbook]:
        """Get all cookbooks that contain a specific meal."""
        return [cb for cb in self.cookbooks.values() if meal_id in cb.meal_ids]
    
    def get_cookbook_count(self) -> int:
        """Get total number of cookbooks."""
        return len(self.cookbooks)
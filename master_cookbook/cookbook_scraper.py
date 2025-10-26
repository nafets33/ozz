import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
from urllib.parse import urlparse
import json
import os
from dotenv import load_dotenv

from master_ozz.utils import llm_assistant_response, print_line_of_error

load_dotenv()

class RecipeScraper:
    """
    A class to scrape recipe information from various recipe websites using LLM extraction.
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def scrape_recipe(self, url: str, llm_parse=True) -> Optional[Dict]:
        """
        Scrape recipe information from a URL using LLM to extract structured data.
        
        Args:
            url: The URL of the recipe page
            show_data_only: If True, only show the extracted data without additional context
            
        Returns:
            Dictionary containing recipe information or None if scraping fails
        """
        try:
            # Fetch the webpage
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # First try JSON-LD (still useful as it's structured)
            recipe_data = self._extract_from_json_ld(soup)
            
            if recipe_data:
                recipe_data['source_url'] = url
                recipe_data['source_domain'] = urlparse(url).netloc
                return recipe_data
            
            # If JSON-LD fails, extract all text and use LLM
            page_text = self._extract_page_text(soup)
            
            if not page_text or len(page_text) < 100:
                print("Not enough text content found on page")
                return None
            if not llm_parse:
                print("Extracting page data only...")
                return page_text

            # Use LLM to extract recipe data
            recipe_data = self._extract_with_llm(page_text, url)
            
            if recipe_data:
                recipe_data['source_url'] = url
                recipe_data['source_domain'] = urlparse(url).netloc
                
            return recipe_data
            
        except requests.RequestException as e:
            print(f"Error fetching URL: {e}")
            return None
        except Exception as e:
            print(f"Error scraping recipe: {e}")
            print_line_of_error(e)
            return None
    
    def _extract_page_text(self, soup: BeautifulSoup) -> str:
        """
        Extract clean text content from the page, removing scripts, styles, etc.
        """
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Limit text length to avoid token limits (roughly 12000 tokens = 48000 chars)
        if len(text) > 40000:
            text = text[:40000] + "\n... [content truncated]"
        
        return text
    
    def _extract_with_llm(self, page_text: str, url: str) -> Optional[Dict]:
        """
        Use your existing llm_assistant_response function to extract structured recipe data from page text.
        """
        try:
            prompt = f"""Extract recipe information from the following webpage text and return it as a JSON object.

The JSON should have these fields:
- name: Recipe name (string)
- description: Brief description of the recipe (string)
- ingredients: List of ingredients with quantities (array of strings)
- prep_instructions: Step-by-step cooking instructions (string, use newlines to separate steps)
- prep_time_minutes: Total prep/cook time in minutes (integer or null)
- servings: Number of servings (integer or null)
- calories: Calories per serving (integer or null)
- other_tags: Relevant tags like cuisine type, dietary restrictions, meal type (array of strings)
- category: One of: breakfast, lunch, dinner, snack, or dessert (string)

If any information is not found, use null or empty array as appropriate.
Return ONLY the JSON object, no other text.

Webpage URL: {url}

Webpage Text:
{page_text}
"""
            
            # Build conversation history for LLM
            conversation_history = [
                {"role": "system", "content": "You are a helpful assistant that extracts structured recipe information from text. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ]
            
            # Use your existing llm_assistant_response function
            assistant_reply = llm_assistant_response(conversation_history)
            
            if not assistant_reply:
                print("No response from LLM")
                return None
            
            # Extract JSON from response
            content = assistant_reply.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = re.sub(r'^```json?\s*', '', content)
                content = re.sub(r'\s*```$', '', content)
            
            recipe_data = json.loads(content)
            
            # Validate required fields
            if not recipe_data.get('name') or not recipe_data.get('ingredients'):
                print("LLM extraction failed to find required fields")
                return None
            
            # Ensure category is valid
            valid_categories = ['breakfast', 'lunch', 'dinner', 'snack', 'dessert']
            if recipe_data.get('category') and recipe_data['category'].lower() not in valid_categories:
                recipe_data['category'] = self._guess_category(recipe_data)
            
            return recipe_data
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            print(f"LLM Response: {assistant_reply}")
            return None
        except Exception as e:
            print(f"Error calling LLM: {e}")
            print_line_of_error(e)
            return None
    
    def _extract_from_json_ld(self, soup: BeautifulSoup) -> Optional[Dict]:
        """
        Extract recipe data from JSON-LD structured data (Schema.org).
        This is still useful as it's already structured data.
        """
        try:
            scripts = soup.find_all('script', type='application/ld+json')
            
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    
                    if isinstance(data, list):
                        recipes = [item for item in data if item.get('@type') == 'Recipe']
                        if recipes:
                            data = recipes[0]
                    
                    if data.get('@type') == 'Recipe':
                        return self._parse_schema_recipe(data)
                        
                except (json.JSONDecodeError, KeyError):
                    continue
                    
        except Exception as e:
            print(f"Error extracting JSON-LD: {e}")
            
        return None
    
    def _parse_schema_recipe(self, data: Dict) -> Dict:
        """Parse Schema.org Recipe structured data."""
        recipe = {}
        
        recipe['name'] = data.get('name', '')
        recipe['description'] = data.get('description', '')
        
        # Ingredients
        ingredients = data.get('recipeIngredient', [])
        if isinstance(ingredients, str):
            ingredients = [ingredients]
        recipe['ingredients'] = ingredients
        
        # Instructions
        instructions = data.get('recipeInstructions', [])
        if isinstance(instructions, str):
            recipe['prep_instructions'] = instructions
        elif isinstance(instructions, list):
            instruction_text = []
            for inst in instructions:
                if isinstance(inst, str):
                    instruction_text.append(inst)
                elif isinstance(inst, dict):
                    if inst.get('text'):
                        instruction_text.append(inst['text'])
                    elif inst.get('@type') == 'HowToStep' and inst.get('text'):
                        instruction_text.append(inst['text'])
            recipe['prep_instructions'] = '\n'.join(instruction_text)
        else:
            recipe['prep_instructions'] = ''
        
        # Times
        if 'prepTime' in data:
            recipe['prep_time_minutes'] = self._parse_duration(data['prepTime'])
        elif 'totalTime' in data:
            recipe['prep_time_minutes'] = self._parse_duration(data['totalTime'])
        
        # Servings
        if 'recipeYield' in data:
            yield_val = data['recipeYield']
            if isinstance(yield_val, list):
                yield_val = yield_val[0] if yield_val else ''
            recipe['servings'] = self._extract_number(str(yield_val))
        
        # Calories
        if 'nutrition' in data and isinstance(data['nutrition'], dict):
            calories_str = data['nutrition'].get('calories', '')
            recipe['calories'] = self._extract_number(calories_str)
        
        # Image
        if 'image' in data:
            image = data['image']
            if isinstance(image, list):
                image = image[0]
            if isinstance(image, dict):
                recipe['image_url'] = image.get('url', '')
            else:
                recipe['image_url'] = str(image)
        
        # Category/Tags
        recipe['other_tags'] = []
        if 'recipeCategory' in data:
            category = data['recipeCategory']
            if isinstance(category, list):
                recipe['other_tags'].extend(category)
            else:
                recipe['other_tags'].append(category)
        
        if 'recipeCuisine' in data:
            cuisine = data['recipeCuisine']
            if isinstance(cuisine, list):
                recipe['other_tags'].extend(cuisine)
            else:
                recipe['other_tags'].append(cuisine)
        
        if 'keywords' in data:
            keywords = data['keywords']
            if isinstance(keywords, str):
                recipe['other_tags'].extend([k.strip() for k in keywords.split(',')])
            elif isinstance(keywords, list):
                recipe['other_tags'].extend(keywords)
        
        # Guess category
        recipe['category'] = self._guess_category(recipe)
        
        return recipe
    
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse ISO 8601 duration string to minutes."""
        if not duration_str:
            return None
            
        try:
            duration_str = duration_str.replace('PT', '')
            hours = 0
            minutes = 0
            
            hour_match = re.search(r'(\d+)H', duration_str)
            if hour_match:
                hours = int(hour_match.group(1))
            
            minute_match = re.search(r'(\d+)M', duration_str)
            if minute_match:
                minutes = int(minute_match.group(1))
            
            return hours * 60 + minutes
            
        except Exception:
            return None
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract the first number from a string."""
        if not text:
            return None
            
        match = re.search(r'\d+', str(text))
        return int(match.group()) if match else None
    
    def _guess_category(self, recipe_data: Dict) -> str:
        """Guess the meal category based on recipe data."""
        name = recipe_data.get('name', '').lower()
        tags = [tag.lower() for tag in recipe_data.get('other_tags', [])]
        all_text = name + ' ' + ' '.join(tags)
        
        breakfast_keywords = ['breakfast', 'pancake', 'waffle', 'oatmeal', 'cereal', 
                             'toast', 'eggs', 'omelet', 'bacon', 'brunch', 'muffin']
        
        dinner_keywords = ['dinner', 'steak', 'roast', 'casserole', 'pasta', 
                          'chicken', 'beef', 'pork', 'seafood', 'salmon']
        
        snack_keywords = ['snack', 'appetizer', 'dessert', 'cookie', 'cake', 
                         'pie', 'brownie', 'bar', 'sweet', 'treat']
        
        if any(keyword in all_text for keyword in breakfast_keywords):
            return 'breakfast'
        elif any(keyword in all_text for keyword in snack_keywords):
            return 'snack'
        elif any(keyword in all_text for keyword in dinner_keywords):
            return 'dinner'
        else:
            return 'lunch'


def scrape_recipe_from_url(url: str) -> Optional[Dict]:
    """
    Convenience function to scrape a recipe from a URL using LLM extraction.
    
    Args:
        url: The URL of the recipe page
        
    Returns:
        Dictionary with recipe data
    """
    scraper = RecipeScraper()
    data = scraper.scrape_recipe(url)
    return data
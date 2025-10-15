"""
Data Collection Script
Scrape and collect product images for the visual search database
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import time
from PIL import Image
import io
import hashlib

class DataCollector:
    """
    Collect product images from various free sources
    
    Sources:
    - Unsplash (free images)
    - Wikimedia Commons (CC0 images)
    - Open Images Dataset (subset)
    """
    
    def __init__(self, output_dir='data/products'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.output_dir / 'metadata.json'
        self.metadata = self.load_metadata()
    
    def load_metadata(self):
        """Load existing metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_metadata(self):
        """Save metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def download_from_unsplash(self, query, count=10):
        """
        Download images from Unsplash
        
        Note: For production, use Unsplash API (free tier: 50 requests/hour)
        https://unsplash.com/developers
        
        Args:
            query: Search query
            count: Number of images
        """
        print(f"📷 Downloading {count} images from Unsplash: '{query}'")
        
        # This is a simplified example
        # For production, use: pip install unsplash-python
        # And get free API key from Unsplash
        
        unsplash_api_url = "https://api.unsplash.com/search/photos"
        
        # You need to get a free API key from Unsplash
        api_key = "YOUR_UNSPLASH_API_KEY"  # Replace with your key
        
        if api_key == "YOUR_UNSPLASH_API_KEY":
            print("⚠️  Please get free Unsplash API key from https://unsplash.com/developers")
            return []
        
        headers = {"Authorization": f"Client-ID {api_key}"}
        
        downloaded = []
        
        for page in range(1, (count // 10) + 2):
            params = {
                "query": query,
                "page": page,
                "per_page": 10
            }
            
            response = requests.get(unsplash_api_url, headers=headers, params=params)
            
            if response.status_code != 200:
                print(f"❌ API error: {response.status_code}")
                break
            
            data = response.json()
            
            for item in data.get('results', [])[:count]:
                try:
                    # Download image
                    image_url = item['urls']['regular']
                    image_data = requests.get(image_url).content
                    
                    # Generate ID
                    image_id = hashlib.md5(image_data).hexdigest()
                    
                    # Save image
                    image_path = self.output_dir / f"{image_id}.jpg"
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    
                    # Save metadata
                    self.metadata[image_id] = {
                        'source': 'unsplash',
                        'query': query,
                        'category': query,
                        'author': item['user']['name'],
                        'description': item.get('description', ''),
                        'url': item['links']['html']
                    }
                    
                    downloaded.append(image_id)
                    print(f"  ✓ Downloaded: {image_id}")
                    
                    if len(downloaded) >= count:
                        break
                
                except Exception as e:
                    print(f"  ✗ Error: {str(e)}")
            
            if len(downloaded) >= count:
                break
            
            time.sleep(1)  # Rate limiting
        
        self.save_metadata()
        print(f"✅ Downloaded {len(downloaded)} images")
        return downloaded
    
    def download_coco_subset(self, categories=['chair', 'couch', 'bed'], max_per_category=20):
        """
        Download subset from COCO dataset
        
        COCO is free and open-source
        Full dataset: https://cocodataset.org/
        
        Args:
            categories: List of category names
            max_per_category: Max images per category
        """
        print(f"📦 Downloading COCO subset...")
        
        try:
            from pycocotools.coco import COCO
        except ImportError:
            print("⚠️  Install pycocotools: pip install pycocotools")
            return []
        
        # Download COCO annotations (small file)
        annotations_url = "http://images.cocodataset.org/annotations/annotations_trainval2017.zip"
        
        print("Note: Full COCO download requires ~25GB")
        print("For MVP, use smaller dataset or API")
        
        # Simplified: Download a few sample images
        coco_samples = [
            "http://images.cocodataset.org/val2017/000000000139.jpg",
            "http://images.cocodataset.org/val2017/000000000285.jpg",
        ]
        
        downloaded = []
        
        for url in coco_samples[:5]:  # Limit for demo
            try:
                response = requests.get(url)
                image_data = response.content
                
                image_id = hashlib.md5(image_data).hexdigest()
                image_path = self.output_dir / f"{image_id}.jpg"
                
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                self.metadata[image_id] = {
                    'source': 'coco',
                    'category': 'various',
                    'url': url
                }
                
                downloaded.append(image_id)
                print(f"  ✓ Downloaded: {image_id}")
                
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
        
        self.save_metadata()
        return downloaded
    
    def scrape_ecommerce(self, url, product_name):
        """
        Scrape product images from e-commerce site
        
        ⚠️ WARNING: Always check robots.txt and terms of service
        Only scrape publicly available data
        Use rate limiting
        
        Args:
            url: Product page URL
            product_name: Product name
        """
        print(f"🛒 Scraping e-commerce: {product_name}")
        
        try:
            # Add user agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Educational Research Bot)'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find images (common selectors)
            image_selectors = [
                'img.product-image',
                'img[data-src]',
                'img.main-image',
                '.product-gallery img'
            ]
            
            downloaded = []
            
            for selector in image_selectors:
                images = soup.select(selector)
                
                for img in images[:3]:  # Limit to 3 per product
                    img_url = img.get('src') or img.get('data-src')
                    
                    if not img_url or img_url.startswith('data:'):
                        continue
                    
                    # Make URL absolute
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        from urllib.parse import urljoin
                        img_url = urljoin(url, img_url)
                    
                    try:
                        img_data = requests.get(img_url, headers=headers, timeout=5).content
                        
                        # Validate image
                        Image.open(io.BytesIO(img_data)).verify()
                        
                        image_id = hashlib.md5(img_data).hexdigest()
                        image_path = self.output_dir / f"{image_id}.jpg"
                        
                        with open(image_path, 'wb') as f:
                            f.write(img_data)
                        
                        self.metadata[image_id] = {
                            'source': 'ecommerce',
                            'product': product_name,
                            'url': url,
                            'image_url': img_url
                        }
                        
                        downloaded.append(image_id)
                        print(f"  ✓ Downloaded: {image_id}")
                        
                        time.sleep(2)  # Rate limiting
                        
                    except Exception as e:
                        print(f"  ✗ Error downloading image: {str(e)}")
                
                if downloaded:
                    break
            
            self.save_metadata()
            return downloaded
            
        except Exception as e:
            print(f"❌ Scraping error: {str(e)}")
            return []
    
    def index_to_database(self, api_url='http://localhost:8000'):
        """
        Index all collected images to vector database
        
        Args:
            api_url: Backend API URL
        """
        print(f"\n📊 Indexing images to database...")
        
        images = list(self.output_dir.glob('*.jpg'))
        indexed = 0
        
        for image_path in images:
            image_id = image_path.stem
            
            if image_id not in self.metadata:
                continue
            
            try:
                # Read image
                with open(image_path, 'rb') as f:
                    files = {'file': f}
                    data = {
                        'metadata': json.dumps(self.metadata[image_id])
                    }
                    
                    response = requests.post(
                        f"{api_url}/index",
                        files=files,
                        data=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        indexed += 1
                        print(f"  ✓ Indexed: {image_id}")
                    else:
                        print(f"  ✗ Failed: {image_id}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"  ✗ Error indexing {image_id}: {str(e)}")
        
        print(f"\n✅ Indexed {indexed}/{len(images)} images")
    
    def get_stats(self):
        """Get collection statistics"""
        images = list(self.output_dir.glob('*.jpg'))
        
        sources = {}
        categories = {}
        
        for image_id in self.metadata:
            source = self.metadata[image_id].get('source', 'unknown')
            category = self.metadata[image_id].get('category', 'unknown')
            
            sources[source] = sources.get(source, 0) + 1
            categories[category] = categories.get(category, 0) + 1
        
        return {
            'total_images': len(images),
            'sources': sources,
            'categories': categories
        }


def main():
    """Example usage"""
    print("="*60)
    print("Data Collection for Visual Search Engine")
    print("="*60)
    
    collector = DataCollector()
    
    # Example 1: Download from Unsplash (requires API key)
    # collector.download_from_unsplash('furniture chair', count=10)
    # collector.download_from_unsplash('furniture sofa', count=10)
    
    # Example 2: Download COCO samples
    collector.download_coco_subset()
    
    # Example 3: Scrape e-commerce (use responsibly!)
    # collector.scrape_ecommerce(
    #     'https://example-store.com/product/chair',
    #     'Modern Office Chair'
    # )
    
    # Show statistics
    stats = collector.get_stats()
    print(f"\n📊 Collection Statistics:")
    print(f"  Total images: {stats['total_images']}")
    print(f"  Sources: {stats['sources']}")
    print(f"  Categories: {stats['categories']}")
    
    # Index to database
    print("\n💾 Index to database? (y/n): ", end='')
    choice = input().strip().lower()
    
    if choice == 'y':
        collector.index_to_database()
    
    print("\n✅ Data collection complete!")
    print("\n📝 Tips:")
    print("  • Always respect robots.txt and terms of service")
    print("  • Use rate limiting to avoid overwhelming servers")
    print("  • Only use data you have rights to use")
    print("  • Check data licenses (CC0, CC-BY, etc.)")

if __name__ == "__main__":
    main()


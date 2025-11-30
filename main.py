import configparser
import os
import requests
import json
import base64
from io import BytesIO

# Add LeetCode base URL constants
LEETCODE_BASEURL = "https://leetcode.com"
LEETCODE_CN_BASEURL = "https://leetcode.cn"

def get_user_badges(username):
    """
    Get badge information for a LeetCode user
    """
    # LeetCode GraphQL query
    query = """
    query userBadges($username: String!) {
      matchedUser(username: $username) {
        badges {
          id
          name
          shortName
          displayName
          icon
          hoverText
          creationDate
          medal {
            slug
            config {
              iconGif
              iconGifBackground
            }
          }
        }
      }
    }
    """
    
    # Request headers
    headers = {
        'Content-Type': 'application/json',
    }
    
    # Request data
    data = {
        'query': query,
        'variables': {
            'username': username
        }
    }
    
    # Send POST request to LeetCode GraphQL API
    response = requests.post('https://leetcode.com/graphql', json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if 'errors' in result:
            print("Error fetching badges:", result['errors'])
            return []
        
        badges = result['data']['matchedUser']['badges']
        for badge in badges:
            if badge['icon'].startswith("/static/"):
                badge['icon'] = LEETCODE_BASEURL + badge['icon']
            if badge['medal']['config']['iconGif'].startswith("/static/"):
                badge['medal']['config']['iconGif'] = LEETCODE_BASEURL + badge['medal']['config']['iconGif']
        return badges
    else:
        print(f"HTTP Error: {response.status_code}")
        return []

def get_user_badges_cn(username):
    """
    Get badge information for a LeetCode China site user
    """
    # LeetCode China site GraphQL query
    query = """
    query userBadges($userSlug: String!, $limit: Int, $skip: Int) {
      userProfileUserMedals(userSlug: $userSlug, limit: $limit, skip: $skip) {
        ...medalNodeFragment
      }
      userProfileUserNextMedal(userSlug: $userSlug) {
        ...medalNodeFragment
      }
    }
    
    fragment medalNodeFragment on MedalNodeV2 {
      slug
      name
      obtainDate
      category
      config {
        icon
        iconGif
        iconGifBackground
      }
      progress
      id
      year
      month
    }
    """
    
    # Request headers
    headers = {
        'Content-Type': 'application/json',
    }
    
    # Request data
    data = {
        'query': query,
        'variables': {
            'userSlug': username,
            'limit': 100,
            'skip': 0
        }
    }
    
    # Send POST request to LeetCode China site GraphQL API
    response = requests.post('https://leetcode.cn/graphql', json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if 'errors' in result:
            print("Error fetching badges:", result['errors'])
            return []
        
        # Get earned badges
        badges = result['data']['userProfileUserMedals']
        
        # Process badge data to make it compatible with international site format
        processed_badges = []
        for badge in badges:
            processed_badge = {
                'id': str(badge['id']),
                'name': badge['name'],
                'shortName': badge['name'],
                'displayName': badge['name'],
                'icon': badge['config']['icon'] if badge['config']['icon'].startswith('http') else LEETCODE_CN_BASEURL + badge['config']['icon'],
                'hoverText': badge['name'],
                'creationDate': badge['obtainDate'].split('T')[0] if badge['obtainDate'] else 'Unknown Date',
                'medal': {
                    'slug': badge['slug'],
                    'config': {
                        'iconGif': badge['config']['iconGif'] if badge['config']['iconGif'].startswith('http') else LEETCODE_CN_BASEURL + badge['config']['iconGif'],
                        'iconGifBackground': badge['config']['iconGifBackground'] if 'iconGifBackground' in badge['config'] and badge['config']['iconGifBackground'].startswith('http') else ''
                    }
                }
            }
            processed_badges.append(processed_badge)
            
        return processed_badges
    else:
        print(f"HTTP Error: {response.status_code}")
        return []

def create_svg_from_badge(badge,animated):
    """
    Create SVG based on badge information
    """
    badge_name = badge.get('displayName', 'Unknown Badge')
    creation_date = badge.get('creationDate', 'Unknown Date')
    if animated:
        icon_url = badge.get('medal', {}).get('config', {}).get('iconGif')
    else:
        icon_url = badge.get('icon', '')
    
    # Download and encode icon as base64 if icon URL exists
    icon_data = ""
    if icon_url and icon_url != LEETCODE_BASEURL:
        try:
            response = requests.get(icon_url)
            if response.status_code == 200:
                # Encode image as base64
                icon_base64 = base64.b64encode(response.content).decode('utf-8')
                # Determine image type
                content_type = response.headers.get('content-type', 'image/png')
                icon_data = f"data:{content_type};base64,{icon_base64}"
        except Exception as e:
            print(f"Error downloading icon: {e}")
    
    # Create SVG content with icon
    if icon_data:
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="400" height="100">
  <rect x="0" y="0" width="400" height="100" fill="#f0f0f0" rx="10"/>
  <text x="20" y="30" font-family="Arial" font-size="16" fill="#333">{badge_name}</text>
  <text x="20" y="60" font-family="Arial" font-size="14" fill="#666">Earned: {creation_date}</text>
  <text x="20" y="85" font-family="Arial" font-size="12" fill="#999">LeetCode Badge</text>
  <image x="320" y="25" width="50" height="50" xlink:href="{icon_data}"/>
</svg>'''
    else:
        # Fallback option without icon
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="300" height="100">
  <rect x="0" y="0" width="300" height="100" fill="#f0f0f0" rx="10"/>
  <text x="20" y="30" font-family="Arial" font-size="16" fill="#333">{badge_name}</text>
  <text x="20" y="60" font-family="Arial" font-size="14" fill="#666">Earned: {creation_date}</text>
  <text x="20" y="85" font-family="Arial" font-size="12" fill="#999">LeetCode Badge</text>
</svg>'''
    
    return svg_content

def create_combined_svg(badges, animated=False):
    """
    Create a combined SVG based on all badge information
    """
    # Calculate SVG dimensions - 2 badges per row, each badge 120px high
    badges_per_row = 2
    rows = (len(badges) + badges_per_row - 1) // badges_per_row
    svg_width = 800
    svg_height = max(120 * rows, 120)
    
    # Start building SVG content
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{svg_width}" height="{svg_height}">
  <rect x="0" y="0" width="{svg_width}" height="{svg_height}" fill="#ffffff"/>'''
    
    # Create display area for each badge
    for i, badge in enumerate(badges):
        row = i // badges_per_row
        col = i % badges_per_row
        
        # Calculate position
        x_offset = col * 400
        y_offset = row * 120
        
        badge_name = badge.get('displayName', 'Unknown Badge')
        creation_date = badge.get('creationDate', 'Unknown Date')
        
        # Get icon URL
        if animated:
            icon_url = badge.get('medal', {}).get('config', {}).get('iconGif')
        else:
            icon_url = badge.get('icon', '')
        
        # Download and encode icon
        icon_data = ""
        if icon_url and icon_url != LEETCODE_BASEURL:
            try:
                response = requests.get(icon_url)
                if response.status_code == 200:
                    # Encode image as base64
                    icon_base64 = base64.b64encode(response.content).decode('utf-8')
                    # Determine image type
                    content_type = response.headers.get('content-type', 'image/png')
                    icon_data = f"data:{content_type};base64,{icon_base64}"
            except Exception as e:
                print(f"Error downloading icon: {e}")
        
        # Add badge display area
        svg_content += f'''
  <g transform="translate({x_offset}, {y_offset})">
    <rect x="10" y="10" width="380" height="100" fill="#f0f0f0" rx="10"/>
    <text x="20" y="35" font-family="Arial" font-size="16" fill="#333">{badge_name}</text>
    <text x="20" y="65" font-family="Arial" font-size="14" fill="#666">Earned: {creation_date}</text>
    <text x="20" y="90" font-family="Arial" font-size="12" fill="#999">LeetCode Badge</text>'''
        
        # Add icon if available
        if icon_data:
            svg_content += f'''
    <image x="320" y="25" width="50" height="50" xlink:href="{icon_data}"/>'''
        
        svg_content += '''
  </g>'''
    
    # End SVG
    svg_content += '''
</svg>'''
    
    return svg_content

def save_svg_to_file(svg_content, filename):
    """
    Save SVG content to file
    """
    # Ensure img directory exists
    os.makedirs('img', exist_ok=True)
    
    # Save SVG file
    filepath = os.path.join('img', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"Saved SVG to {filepath}")

def main():
    # Read configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Get username and site settings
    username = config.get('LEETCODE', 'username')
    site = config.get('LEETCODE', 'site', fallback='leetcode.com')  # Default to international site
    # Whether to use animated icons
    animated = config.getboolean('LEETCODE', 'animated',fallback=False)
    
    if not username:
        print("Please set your LeetCode username in config.ini")
        return
    
    print(f"Fetching badges for user: {username} on {site}")
    
    # Get badge information based on site
    if site == 'leetcode.cn':
        badges = get_user_badges_cn(username)
    else:
        badges = get_user_badges(username)
    
    if not badges:
        print("No badges found or error occurred.")
        return
    
    print(f"Found {len(badges)} badges. Creating combined SVG...")
    
    # Create SVG file with all badges
    combined_svg_content = create_combined_svg(badges, animated)
    save_svg_to_file(combined_svg_content, f"{username}_{site.replace('.', '_')}_badges.svg")
    
    print("Combined SVG with all badges has been created.")

if __name__ == "__main__":
    main()
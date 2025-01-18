import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

import logging

logging.basicConfig(level=logging.INFO)
def scrape_course(subj_code, course_num, term="202502"):
    """
    Scrapes course information from Georgia Tech's course catalog
    
    Args:
        subj_code (str): Subject code (e.g., 'MATH')
        course_num (str): Course number (e.g., '3235')
        term (str): Term code (default: '202502' for Spring 2025)
    """
    base_url = "https://oscar.gatech.edu/bprod/bwckctlg.p_disp_course_detail"
    params = {
        "cat_term_in": term,
        "subj_code_in": subj_code,
        "crse_numb_in": course_num
    }
    
    try:
        # Make the request
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find course title
        title_element = soup.find('td', class_='nttitle')
        title = title_element.text.strip() if title_element else "Title not found"
        
        # Initialize variables
        desc_element = soup.find('td', class_='ntdefault')
        description = "Description not found"
        prereq_text = None
        content_element = None
        prerequisites = "No prerequisites found"
        
        if desc_element:
            description = desc_element.get_text().split('\n')[1].strip()
            
            # Find prerequisites section
            prereq_section = desc_element.find(text=re.compile('Prerequisites:'))
            if prereq_section:
                next_element = prereq_section.find_next('br')
                if next_element and next_element.next_sibling:
                    prereq_text = next_element.next_sibling.strip()
        
        content_element = soup.find('td', class_='ntdefault')
        if content_element:
            content_text = content_element.get_text('\n')
            content_lines = content_text.split('\n')
            
            # Get description if not found earlier
            if description == "Description not found":
                description = next((line.strip() for line in content_lines if line.strip()), "Description not found")
            
            # Find prerequisites using course numbers pattern
            prereq_pattern = r'[1-9]\d{3}'
            prereq_matches = re.finditer(prereq_pattern, content_text)
            
            # Get unique course numbers with their subject codes
            prereq_courses = set()
            for match in prereq_matches:
                preceding_text = content_text[max(0, match.start() - 10):match.start()]
                subj_match = re.search(r'[A-Z]{2,4}\s*$', preceding_text)
                if subj_match:
                    course = f"{subj_match.group().strip()} {match.group()}"
                    prereq_courses.add(course)
            
            prerequisites = list(prereq_courses) if prereq_courses else []
        
        return {
            "title": title,
            "description": description,
            "prerequisites": prerequisites
        }
        
    except requests.RequestException as e:
        return {
            "error": f"Failed to fetch course data: {str(e)}",
            "title": None,
            "description": None,
            "prerequisites": None
        }

def get_all_math_courses():
    lst = ['0399', '0999', '1111', '1113', '1501', '1503', '1504', '1512', '1550', '1551', '1552', '1553', '1554', '1555', '1564', '1601', '1711', '1712', '1803', '2106', '2406', '2550', '2551', '2552', '2561', '2562', '2603', '2605', '2801', '2802', '2803', '2804', '2805', '3012', '3022', '3215', '3225', '3235', '3236', '3406', '3670', '3801', '3802', '3803', '3804', '3805', '4012', '4022', '4032', '4080', '4090', '4107', '4108', '4150', '4210', '4221', '4222', '4255', '4261', '4262', '4280', '4305', '4317', '4318', '4320', '4347', '4348', '4431', '4432', '4441', '4541', '4542', '4580', '4581', '4640', '4641', '4755', '4777', '4782', '4801', '4802', '4803', '4804', '4805', '4873', '6001', '6014', '6021', '6112', '6121', '6122', '6221', '6235', '6241', '6242', '6262', '6263', '6266', '6267', '6307', '6308', '6321', '6337', '6338', '6341', '6342', '6421', '6422', '6441', '6442', '6451', '6452', '6453', '6455', '6456', '6514', '6579', '6580', '6583', '6584', '6635', '6640', '6641', '6643', '6644', '6645', '6646', '6647', '6701', '6702', '6705', '6710', '6711', '6759', '6761', '6762', '6767', '6769', '6783', '6785', '6793', '7012', '7014', '7016', '7018', '7244', '7245', '7251', '7252', '7337', '7338', '7339', '7510', '7581', '7586', '8305', '8306', '8307', '8801', '8802', '8803', '8804', '8805', '8811', '8812', '8813', '8814', '8815', '8821', '8822', '8823', '8824', '8825', '8831', '8832', '8833', '8834', '8835', '8841', '8842', '8843', '8844', '8845', '8851', '8852', '8853', '8854', '8855', '8863', '8873']

    tmp_df = pd.DataFrame()
    for x in lst:
        # tmp_df = tmp_df.append(scrape_course('MATH', x), ignore_index=True)
        z = scrape_course('MATH', x)
        print(z)
        tmp_df = pd.concat([tmp_df, pd.DataFrame([z])])

    tmp_df.to_csv('gt_math_courses.csv', index=False)

# Example usage
if __name__ == "__main__":
    # Example: Scrape MATH 3235
    # result = scrape_course("CS", "1331")

    get_all_math_courses()
    
    print("\nCourse Information:")
    # print("-" * 50)
    # for key, value in result.items():
    #     print(f"{key.capitalize()}:")
    #     print(f"{value}\n")
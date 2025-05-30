import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

import logging

logging.basicConfig(level=logging.INFO)

def extract_prerequisites(text: str) -> tuple[list[str], list[str]]:
    """
    Extract prerequisites from course text, separating must-have and optional prerequisites.
    Returns (must_have_prerequisites, optional_prerequisites)
    
    Handles complex cases like:
    - "MATH 4107 and one of MATH 2406, MATH 4305, or permission of instructor"
    - "MATH 3012 or MATH 3022 and MATH 2106"
    - Multiple AND/OR combinations
    """
    if not text:
        return [], []
    
    # Regular expression to find course numbers with department
    course_pattern = r'([A-Z]{2,4})\s*(\d{4})'
    
    # Initialize lists for both types of prerequisites
    must_have_prereqs = []
    optional_prereqs = []
    
    # First pass: Split by 'and' to separate mandatory parts
    and_parts = [part.strip() for part in text.split(' and ')]
    
    for part in and_parts:
        part_lower = part.lower()
        
        # Check for "one of" pattern first
        if 'one of' in part_lower:
            # Everything after "one of" is optional
            one_of_idx = part_lower.find('one of')
            before_one_of = part[:one_of_idx].strip()
            after_one_of = part[one_of_idx + 7:].strip()
            
            # Check for any must-have prerequisites before "one of"
            if before_one_of:
                matches = re.finditer(course_pattern, before_one_of)
                for match in matches:
                    course = f"{match.group(1)} {match.group(2)}"
                    if course not in must_have_prereqs:
                        must_have_prereqs.append(course)
            
            # Add all courses after "one of" as optional
            matches = re.finditer(course_pattern, after_one_of)
            for match in matches:
                course = f"{match.group(1)} {match.group(2)}"
                if course not in optional_prereqs and course not in must_have_prereqs:
                    optional_prereqs.append(course)
        
        # Check for simple OR pattern
        elif ' or ' in part_lower:
            matches = re.finditer(course_pattern, part)
            for match in matches:
                course = f"{match.group(1)} {match.group(2)}"
                if course not in optional_prereqs and course not in must_have_prereqs:
                    optional_prereqs.append(course)
        
        # Must-have prerequisites (no OR/one of)
        else:
            matches = re.finditer(course_pattern, part)
            for match in matches:
                course = f"{match.group(1)} {match.group(2)}"
                if course not in optional_prereqs and course not in must_have_prereqs:
                    must_have_prereqs.append(course)
    
    return must_have_prereqs, optional_prereqs

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
                # Get all text after "Prerequisites:"
                full_text = desc_element.get_text()
                prereq_start = full_text.find('Prerequisites:')
                if prereq_start != -1:
                    prereq_text = full_text[prereq_start + len('Prerequisites:'):].strip()
                
                prereq_text = re.sub(r'Undergraduate Semester level\s+(?=[A-Z]{2,4}\s*\d)', '', 
                                     prereq_text, flags=re.IGNORECASE).strip()
                prereq_text = re.sub(r'Graduate Semester level\s+(?=[A-Z]{2,4}\s*\d)', '', 
                                     prereq_text, flags=re.IGNORECASE).strip()
                prereq_text = re.sub(r'Minimum Grade of [SDTABC]', '', prereq_text, flags=re.IGNORECASE).strip()
                prereq_text = re.sub(r'\s+', ' ', prereq_text).strip()
        
        content_element = soup.find('td', class_='ntdefault')
        if content_element:
            content_text = content_element.get_text('\n')
            content_lines = content_text.split('\n')
            
            # Get description if not found earlier
            if description == "Description not found":
                description = next((line.strip() for line in content_lines if line.strip()), "Description not found")
            
            # Initialize prerequisites as empty list
            prerequisites = []
            
            # Only extract prerequisites if prereq_text exists
            if prereq_text:
                # Find prerequisites using course numbers pattern
                prereq_pattern = r'[1-9]\d{3}'
                prereq_matches = re.finditer(prereq_pattern, prereq_text)
                
                # Get unique course numbers with their subject codes
                prereq_courses = set()
                for match in prereq_matches:
                    preceding_text = prereq_text[max(0, match.start() - 10):match.start()]
                    subj_match = re.search(r'[A-Z]{2,4}\s*$', preceding_text)
                    if subj_match:
                        course = f"{subj_match.group().strip()} {match.group()}"
                        prereq_courses.add(course)
                
                prerequisites = list(prereq_courses)
        
        must_have_prereqs, optional_prereqs = extract_prerequisites(prereq_text)
        return {
            "title": title,
            "description": description,
            "prerequisites": prerequisites,
            "prereq_text": prereq_text,
            "must_have_prereqs": must_have_prereqs,
            "optional_prereqs": optional_prereqs
        }
        
    except requests.RequestException as e:
        return {
            "error": f"Failed to fetch course data: {str(e)}",
            "title": None,
            "description": None,
            "prerequisites": None
        }

def get_all_math_courses():
    math_list = ['0399', '0999', '1111', '1113', '1501', '1503', '1504', '1512', '1550', '1551', '1552', '1553', '1554', '1555', '1564', '1601', '1711', '1712', '1803', '2106', '2406', '2550', '2551', '2552', '2561', '2562', '2603', '2605', '2801', '2802', '2803', '2804', '2805', '3012', '3022', '3215', '3225', '3235', '3236', '3406', '3670', '3801', '3802', '3803', '3804', '3805', '4012', '4022', '4032', '4080', '4090', '4107', '4108', '4150', '4210', '4221', '4222', '4255', '4261', '4262', '4280', '4305', '4317', '4318', '4320', '4347', '4348', '4431', '4432', '4441', '4541', '4542', '4580', '4581', '4640', '4641', '4755', '4777', '4782', '4801', '4802', '4803', '4804', '4805', '4873', '6001', '6014', '6021', '6112', '6121', '6122', '6221', '6235', '6241', '6242', '6262', '6263', '6266', '6267', '6307', '6308', '6321', '6337', '6338', '6341', '6342', '6421', '6422', '6441', '6442', '6451', '6452', '6453', '6455', '6456', '6514', '6579', '6580', '6583', '6584', '6635', '6640', '6641', '6643', '6644', '6645', '6646', '6647', '6701', '6702', '6705', '6710', '6711', '6759', '6761', '6762', '6767', '6769', '6783', '6785', '6793', '7012', '7014', '7016', '7018', '7244', '7245', '7251', '7252', '7337', '7338', '7339', '7510', '7581', '7586', '8305', '8306', '8307', '8801', '8802', '8803', '8804', '8805', '8811', '8812', '8813', '8814', '8815', '8821', '8822', '8823', '8824', '8825', '8831', '8832', '8833', '8834', '8835', '8841', '8842', '8843', '8844', '8845', '8851', '8852', '8853', '8854', '8855', '8863', '8873']

    cs_list = [1100, 1171, 1301, 1315, 1316, 1331, 1332, 1371, 1372, 1801, 1802, 1803, 1804, 1805, 2050, 2051, 2110, 2200, 2261, 2316, 2335, 2340, 2345, 2600, 2701, 2801, 2802, 2803, 2804, 2805, 3001, 3101, 3210, 3220, 3235, 3237, 3240, 3251, 3300, 3311, 3312, 3451, 3510, 3511, 3600, 3630, 3651, 3743, 3744, 3750, 3751, 3790, 3801, 3802, 3803, 3804, 3805, 3873, 4001, 4002, 4003, 4005, 4010, 4052, 4057, 4117, 4210, 4220, 4233, 4235, 4237, 4238, 4239, 4240, 4243, 4245, 4251, 4255, 4260, 4261, 4262, 4263, 4265, 4267, 4270, 4280, 4290, 4320, 4330, 4342, 4365, 4392, 4400, 4420, 4423, 4432, 4440, 4452, 4455, 4460, 4464, 4470, 4472, 4475, 4476, 4480, 4488, 4495, 4496, 4497, 4510, 4520, 4530, 4540, 4550, 4560, 4590, 4605, 4611, 4613, 4615, 4616, 4622, 4625, 4632, 4635, 4641, 4644, 4646, 4649, 4650, 4660, 4665, 4670, 4675, 4685, 4690, 4710, 4723, 4725, 4726, 4731, 4741, 4742, 4745, 4752, 4770, 4791, 4792, 4793, 4795, 4801, 4802, 4803, 4804, 4805, 4816, 4851, 4853, 4854, 4863, 4873, 4883, 4893, 4912, 6010, 6035, 6150, 6200, 6210, 6211, 6220, 6230, 6235, 6238, 6239, 6241, 6245, 6246, 6250, 6255, 6260, 6261, 6262, 6263, 6264, 6265, 6266, 6267, 6268, 6269, 6280, 6290, 6291, 6300, 6301, 6310, 6320, 6330, 6340, 6365, 6390, 6400, 6402, 6411, 6421, 6422, 6423, 6430, 6435, 6440, 6441, 6451, 6452, 6454, 6455, 6456, 6457, 6460, 6461, 6465, 6470, 6471, 6474, 6475, 6476, 6480, 6485, 6491, 6492, 6497, 6505, 6515, 6520, 6550, 6601, 6603, 6641, 6670, 6675, 6705, 6725, 6726, 6727, 6730, 6745, 6747, 6750, 6753, 6754, 6755, 6756, 6763, 6764, 6770, 6780, 6795, 7001, 7110, 7210, 7230, 7250, 7260, 7270, 7280, 7292, 7400, 7450, 7451, 7455, 7460, 7465, 7467, 7470, 7476, 7490, 7491, 7492, 7495, 7496, 7497, 7499, 7510, 7520, 7525, 7530, 7535, 7540, 7545, 7560, 7610, 7611, 7612, 7613, 7615, 7616, 7620, 7626, 7630, 7631, 7632, 7633, 7634, 7636, 7637, 7638, 7639, 7640, 7641, 7642, 7643, 7644, 7645, 7646, 7647, 7648, 7649, 7650, 7651, 7695, 7697, 7741, 7742, 7743, 7750, 7751, 7785, 7790, 8001, 8002, 8003, 8004, 8005, 8006, 8030, 8741, 8750, 8751, 8795, 8801, 8802, 8803, 8804, 8805, 8806, 8811, 8813, 8816, 8873, 8893]
    
    subject = 'MATH'
    if subject == 'CS':
        subject_list = cs_list
    else:
        subject_list = math_list
    
    import concurrent.futures
    import pandas as pd

    def scrape_course_wrapper(x):
        z = scrape_course(subject, x)
        print(f"Scraping course {x}")
        return z

    # Create thread pool and execute scraping in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all scraping tasks and get futures
        future_to_course = {executor.submit(scrape_course_wrapper, x): x for x in subject_list}
        
        # Collect results as they complete
        results = []
        for future in concurrent.futures.as_completed(future_to_course):
            results.append(future.result())
    
    # Convert results to dataframe and sort by course number
    tmp_df = pd.DataFrame(results)
    tmp_df['number'] = tmp_df['title'].str.extract('(\d+)').astype(int)
    tmp_df = tmp_df.sort_values('number').drop('number', axis=1)
    
    tmp_df.to_csv(f'data2/gt_{subject}_courses.csv', index=False)

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
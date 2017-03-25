from ..wikipedia_scraper.wikipedia_scraper import get_topics_given_profiles

import re
import textract

profile_dict = None


def convert_pdf_to_text(pdf_file_location):
    """
        Convert pdf file to text using textract
    """
    text = textract.process(pdf_file_location)

    return text


def remove_useless_ascii(text):
    """
        Remove multiple spaces, multiple new line, decode and encode in utf-8
    """
    text = text.decode('ascii', 'ignore')
    text = re.sub(r'[^\x00-\x7f]|\n+| +', r' ', text)
    text = text.encode('ascii', 'ignore')
    text = text.lower()
    return text


def get_pre_score(profile_dict, pdf_text):
    """
        From the word list get the repetations in pdf text
        Profile_dict is of the form {'Profile_name' : [(word, word_rank),...]}
        Result is of the form {'Profile_name' : {'word from word list' : (count, word_rank)}}
    """
    result = {}
    for profile_name, word_list in profile_dict.iteritems():
        temp_result = {}
        for word, word_rank in word_list:
            temp_word = ''.join(i.lower() for i in word if i.isalpha() or i == ' ')
            temp_count = len(re.compile(r'\b%s\b' % temp_word, flags=re.IGNORECASE).findall(pdf_text))
            temp_result[word] = (temp_count, word_rank)
        result[profile_name] = temp_result
    # print 'pre score -> ', result
    return result


def get_score(pre_score):
    """
        Get score which is sumation(frequency * word_rank)/summation(word_rank)
    """
    final_score = {}
    for profile_name, value in pre_score.iteritems():
        score_for_profile = 0
        total_rank = 0

        for word, (count, rank) in value.iteritems():
            score_for_profile += (count * rank)
            total_rank += rank

        final_score[profile_name] = score_for_profile / float(total_rank)

    return final_score


def main_score(profile_and_key_words, pdf_file_name):
    """
        Input is of the form {'profile_1' : [key words], 'profile_2' : [key_words]}
    """
    pdf_text = convert_pdf_to_text(pdf_file_name)
    pdf_text = remove_useless_ascii(pdf_text)

    profile_dict = get_topics_given_profiles(profile_and_key_words)
    pre_score = get_pre_score(profile_dict, pdf_text)
    final_score = get_score(pre_score)

    return final_score


def process_resumes_in_bulk(profile, files):
    for f in files:
        print f, main_score(profile, f)


if __name__ == '__main__':
    ## Testing
    file_names = [
        'tests/resumes/Anmol_Resume.pdf',
        'tests/resumes/resume_1.pdf',
        'tests/resumes/resume_2.pdf',
        'tests/resumes/resume_3.pdf',
        'tests/resumes/resume_4.pdf',
        'tests/resumes/resume_5.pdf',
        'tests/resumes/resume_6.pdf',
        'tests/resumes/resume_7.pdf'
    ]
    p = {"Machine Learning": ["Machine Learning", "Artificial Neural Networks"],
         "Cryptography": ["Encryption", "cipher", 'NIST']}

    process_resumes_in_bulk(p, file_names)
    # s = main_score(p, file_name)

import os
import json
import csv
import pdfplumber
from crewai import Agent, Task, Crew, Process, LLM

# ૧. OpenRouter API Key
os.environ["OPENAI_API_KEY"] = "sk-or-v1-50a842fgfgffdgdfgdfgfgfdgdfgdfgfdgdfgdfkukj115hfgh"

# ૨. બજેટ ફ્રેન્ડલી DeepSeek મોડેલ
my_llm = LLM(
    model="openai/deepseek/deepseek-chat",
    base_url="https://openrouter.ai/api/v1",
    temperature=0.1
)

# ૩. PDF માંથી ડેટા વાંચવાનું ફંક્શન
def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        return extracted_text
    except Exception as e:
        return ""

# ૪. એજન્ટ્સ (ટીમ મેમ્બર્સ)
ocr_reader_agent = Agent(
    role='Compliance Auditor',
    goal='ડેટામાં રકમ આંકડામાં અને નિયમો મુજબ સાચી છે કે નહીં તેની ખાતરી કરવી.',
    backstory='તમે ફાઇનાન્સ અને ઓડિટ વિભાગના સિનિયર ઓફિસર છો. તમે કોઈપણ ખોટી એન્ટ્રી પાસ થવા દેતા નથી.',
    verbose=False, # પ્રોસેસિંગ ફાસ્ટ કરવા માટે વાતો (Thoughts) બંધ કરી છે
    allow_delegation=False,
    llm=my_llm
)

auditor_agent = Agent(
    role='Compliance Auditor',
    goal='ડેટામાં રકમ આંકડામાં અને નિયમો મુજબ સાચી છે કે નહીં તેની ખાતરી કરવી.',
    backstory='તમે ફાઇનાન્સ અને ઓડિટ વિભાગના સિનિયર ઓફિસર છો. તમે કોઈપણ ખોટી એન્ટ્રી પાસ થવા દેતા નથી.',
    verbose=False,
    allow_delegation=False,
    llm=my_llm
)

formatter_agent = Agent(
    role='JSON Data Formatter',
    goal='ઓડિટ થયેલા ડેટાને પરફેક્ટ મશીન-રીડેબલ JSON માં કન્વર્ટ કરવો.',
    backstory='તમે બેકએન્ડ ડેવલપર છો, જે કડક નિયમો મુજબ માત્ર JSON જ આઉટપુટ આપે છે.',
    verbose=False,
    allow_delegation=False,
    llm=my_llm
)

# ૫. બૅચ પ્રોસેસિંગ લૂપ (મુખ્ય ઓટોમેશન)
pdf_folder = "PDF_Letters" # તમારા ફોલ્ડરનું નામ
# --- નવો ઉમેરેલો કોડ (ફોલ્ડર ચેક કરવા અને બનાવવા માટે) ---
if not os.path.exists(pdf_folder):
    os.makedirs(pdf_folder)
    print(f"📁 નવું ફોલ્ડર '{pdf_folder}' બનાવવામાં આવ્યું છે. કૃપા કરીને તેમાં સ્કેન કરેલી PDF ફાઈલો મૂકીને સ્ક્રિપ્ટ ફરીથી રન કરો.")
    exit() # ફોલ્ડર હજુ ખાલી જ હોવાથી પ્રોગ્રામ આગળ વધવાને બદલે અહીં જ બંધ થઈ જશે
    # -----------------------------------------------------------
all_results = [] # બધા ડેટા ભેગા કરવાનું લિસ્ટ

print(f"🚀 ફોલ્ડર '{pdf_folder}' માંથી ફાઈલો વાંચવાનું શરૂ...")

# ફોલ્ડરની દરેક PDF ફાઈલ માટે લૂપ ફરશે
for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        print(f"\n📄 પ્રોસેસિંગ ચાલુ છે: {filename} ...")
        
        raw_pdf_text = extract_text_from_pdf(pdf_path)
        
        if not raw_pdf_text.strip():
            print(f"⚠️ {filename} માંથી લખાણ મળ્યું નહીં. (સ્કેન ક્વોલિટી ખરાબ હોઈ શકે).")
            continue

        # દરેક ફાઈલ માટે નવા ટાસ્ક
        task1 = Task(
            description=f'આ PDF ના લખાણમાંથી ગ્રાહકનું નામ, સેન્ક્શન નંબર અને મંજૂર રકમ શોધો: \n\n{raw_pdf_text}',
            expected_output='નામ, સેન્ક્શન નંબર અને રકમનું લિસ્ટ.',
            agent=ocr_reader_agent
        )

        task2 = Task(
            description='Task 1 ના ડેટાને ચેક કરો. રકમને માત્ર આંકડામાં (કોમા વગર) ફેરવો.',
            expected_output='વેલિડેટ થયેલો અને સુધારેલો ડેટા.',
            agent=auditor_agent
        )

        task3 = Task(
            description='વેલિડેટ થયેલા ડેટાને નીચે મુજબના ચોક્કસ JSON ફોર્મેટમાં જ ગોઠવો. બીજું કોઈ વધારાનું લખાણ ન હોવું જોઈએ.',
            expected_output='''{"name": "ગ્રાહકનું નામ", "sanction_no": "ફાઈલ નંબર", "amount": 50000}''',
            agent=formatter_agent
        )

        audit_crew = Crew(
            agents=[ocr_reader_agent, auditor_agent, formatter_agent],
            tasks=[task1, task2, task3],
            process=Process.sequential
        )

        # એજન્ટ્સ કામ કરશે
        final_result = audit_crew.kickoff()
        
        # JSON આઉટપુટને પાયથોન ડિક્શનરીમાં ફેરવવાનો પ્રયાસ
        try:
            result_str = str(final_result).strip()
            # જો મોડેલે આઉટપુટમાં ```json લખ્યું હોય તો તેને હટાવવા
            if result_str.startswith("```json"):
                result_str = result_str[7:-3].strip()
            elif result_str.startswith("```"):
                result_str = result_str[3:-3].strip()
                
            parsed_data = json.loads(result_str)
            parsed_data["Source File"] = filename # કઈ ફાઈલનો ડેટા છે તે યાદ રાખવા
            all_results.append(parsed_data)
            print(f"✅ સફળ: {parsed_data.get('name')}")
            
        except Exception as e:
            print(f"❌ {filename} ના JSON માં એરર આવી: {e}")

# ૬. ફાઇનલ ડેટાને પ્યોર પાયથોન વડે CSV (Excel) માં સેવ કરવો
if all_results:
    csv_filename = "Final_Audit_Report.csv"
    keys = all_results[0].keys() # JSON ના હેડિંગ્સ (નામ, રકમ વગેરે) પકડશે
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_results)
        
    print(f"\n🎉 શાનદાર! સિક્યોરિટી બાયપાસ થઈ ગઈ. તમારો ડેટા '{csv_filename}' માં સેવ થઈ ગયો છે!")
else:
    print("\nકોઈ ડેટા એક્સટ્રેક્ટ થઈ શક્યો નથી.")
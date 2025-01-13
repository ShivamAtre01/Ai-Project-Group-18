from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
import pandas as pd
from googletrans import Translator, LANGUAGES

# Initialize translator
translator = Translator()

def load_gita_database(file_path):
    try:
        df = pd.read_csv('Bhagwad_Gita2.csv')
        return df
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        return f"Error loading file: {str(e)}"

def translate_text(text, target_lang):
    try:
        translation = translator.translate(text, dest=target_lang)
        return translation.text
    except Exception as e:
        return f"Translation error: {str(e)}"

def lookup_verse(df, chapter, verse, target_lang='en'):
    try:
        result = df[(df['Chapter'] == chapter) & (df['Verse'] == verse)]
        
        if len(result) == 0:
            return "Verse not found in the database."
        
        hindi_meaning = result['HinMeaning'].iloc[0]
        english_meaning = result['EngMeaning'].iloc[0]
        
        # If target language is Hindi or English, return directly
        if target_lang == 'hi':
            translated_meaning = hindi_meaning
        elif target_lang == 'en':
            translated_meaning = english_meaning
        else:
            # Translate from English to target language
            translated_meaning = translate_text(english_meaning, target_lang)
        
        return {
            'hindi': hindi_meaning,
            'english': english_meaning,
            'translated': translated_meaning,
            'language': LANGUAGES.get(target_lang, 'Unknown')
        }
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Load the database globally
df = load_gita_database('Bhagwad_Gita2.csv')

class GitaHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/lookup'):
            # Parse query parameters
            query = urlparse(self.path).query
            params = parse_qs(query)
            
            try:
                chapter = int(params['chapter'][0])
                verse = int(params['verse'][0])
                target_lang = params.get('language', ['en'])[0]
                
                result = lookup_verse(df, chapter, verse, target_lang)
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(result).encode())
                return
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
                return
        
        elif self.path.startswith('/languages'):
            # Send available languages
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(LANGUAGES).encode())
            return
            
        # Serve static files
        return SimpleHTTPRequestHandler.do_GET(self)

# Start the server
server = HTTPServer(('localhost', 8000), GitaHandler)
print("Server started at http://localhost:8000")
server.serve_forever()
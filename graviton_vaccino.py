# Import necessary libraries
import streamlit as st
from wit import Wit
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import smtplib
import requests
from io import BytesIO
from msrest.authentication import CognitiveServicesCredentials
import os
import uuid
import time
import json
import re
import pandas as pd
import pickle
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
import streamlit.components.v1 as components


# Page configs
st.set_page_config(page_title="Vaccino", page_icon="💉")
st.title("Vaccino 💉")

st.caption("Tip: Say 'help me' to get sample utterances")


# Setup NLP model
client = Wit("JWXHN3M6TIQFKZSOXT53D3ENQ77ROVCK")



# Function for cleaning raw html
def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext


# Voice button
stt_button = Button(label="Click and Speak", width=650, height=40) 

stt_button.js_on_event("button_click", CustomJS(code="""
	var recognition = new webkitSpeechRecognition();
	recognition.continuous = false;
	recognition.interimResults = false;
	
	recognition.start();

	recognition.onresult = function (e) {
		var value = "";
		for (var i = e.resultIndex; i < e.results.length; ++i) {
			if (e.results[i].isFinal) {
				value += e.results[i][0].transcript;
			}
		}
		if ( value != "") {
			document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
		}
	}    
	"""))

# Button event
result = streamlit_bokeh_events(
	stt_button,
	events="GET_TEXT",
	key="listen",
	refresh_on_update=False,
	override_height=75,
	debounce_time=0)


# Processing result
if result:
	if "GET_TEXT" in result:
		st.caption(f'You said: {result.get("GET_TEXT")}')
		# Send query to Wit
		with st.spinner('Talking to Wit'):
			response = client.message(result.get("GET_TEXT"))
		
		# Returned JSON 
		#st.json(response)
		
		try:
			intent = response['intents'][0]['name']
		except:
			intent = ""    


		
		# Notify by Email.
		if intent == 'email_me': 


			entity = response['entities']['wit$number:number']
			entity_list = []
			for y in entity:
				entity_list.append(int(y['body']))

			#st.markdown(entity_list)    

			email = st.text_input("Enter email 📩","",key="0")
			if st.button("Send Mail"):
				if email == "":
					st.error("Please enter both Email and Email Body")
				else:
					me = "sharan.goku19@gmail.com"
					you = email
					text_pass = "sharannarutoshippuden"
					
					msg = MIMEMultipart('alternative')
					msg['Subject'] = "Appointment Details"
					msg['From'] = me
					msg['To'] = you
					
					# &#10;   --> for line break
					base_html = """
					<div style="border: 2px solid red; 
					white-space:pre-wrap; border-radius: 5%; 
					padding: 10px; background-color: lightyellow;
					width:240px;"><b>ID</b>: {} &#10;<b>Center Name</b>: {} &#10;<b>Block Name</b>: {} &#10;<b>Pin Code</b>: {} &#10;<b>Date</b>: {} &#10;<b>Vaccine Name</b>: {} &#10;<b>Capacity</b>: {} &#10;<b>Min. Age</b>: {} &#10;<b>Timing</b>: {} &#10;<b>Fees</b>:{}
					</div>
					<br>
					"""
					

					final_html = ""
					input_df = pd.read_csv('data_file.csv')
					
					for x in entity_list:
						h_name = input_df.loc[x,"Name"]
						b_name = input_df.loc[x,"Block Name"]
						Pin = input_df.loc[x,"Pin"]
						Date = input_df.loc[x,"Date"]
						Vaccine = input_df.loc[x,"Vaccine"]
						Capacity = input_df.loc[x,"Capacity"]
						Age = input_df.loc[x,"Age Limit"]
						Timing = input_df.loc[x,"Timing"]
						Fees = input_df.loc[x,"Fees"]

						final_html += base_html.format(x,h_name,b_name,Pin,Date,Vaccine,Capacity,Age,Timing,Fees)
					final_html += '<br>Book <a href="https://play.google.com/store/apps/details?id=nic.goi.aarogyasetu&hl=en_IN&gl=US">Here</a>.'
					#part3 = MIMEText(end_html, 'html')
					part2 = MIMEText(final_html, 'html')
					msg.attach(part2)
					#msg.attach(part3)


					text_pass = "sharannarutoshippuden"
					
					with st.spinner("Generating Email..."):
						s = smtplib.SMTP("smtp.gmail.com",587)
						s.starttls()
						s.login(me,text_pass)
					with st.spinner("Sending mail..."):
						s.sendmail(me,you,msg.as_string())
						s.quit()
					st.success("Email sent successfully")

		

		# News and tweets related to vaccines
		elif intent == 'vaccine_news':
			st.audio("vaccine_news.wav")
			try:
				res = requests.get("https://api.rootnet.in/covid19-in/stats/latest")  
				res = res.json()
				res = res['data']['summary']
				total_cases = res['total']
				recovered = res['discharged']
				deaths = res['deaths']
				st.title("India Current Covid Stats:")
				st.markdown(f"<b>Total Cases</b>: {total_cases}",unsafe_allow_html=True)
				st.markdown(f"<b>Total Recovered</b>: {recovered}",unsafe_allow_html=True)
				st.markdown(f"<b>Total Deaths</b>: {deaths}",unsafe_allow_html=True)
			except:
				pass    

			subscription_key = "7e1a2f7b90464dbd90e5a4e353e4b3fe"
			headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
			
			search_term = "Vaccine News in India" #Covid Breaking in India
			search_url = "https://api.bing.microsoft.com/v7.0/news/search"
			params  = {"q": search_term, "textDecorations": True, "textFormat": "HTML","count":2}
			response = requests.get(search_url, headers=headers, params=params)
			response.raise_for_status()
			search_results = response.json()

			#st.json(search_results)

			if len(search_results['value'])>0:
				st.title("News Links:")
				for x in search_results['value']:
					st.markdown(f"<b>{cleanhtml(x['name'])}</b>",unsafe_allow_html=True)
					st.markdown(f"{cleanhtml(x['description'])}")
					try:
						st.image(f"{x['image']['thumbnail']['contentUrl']}",width=150)
					except:
						st.info("No Image found")
					st.markdown(f'<a href="{x["url"]}" target="_blank">Link</a>', unsafe_allow_html=True)
					
			else:   
				st.subheader("No relevant news available currently.")

			st.write("")
			st.write("")
			st.write("")

			components.html("""<a class="twitter-timeline"
			href="https://twitter.com/Vaccinate4Life" 
			data-tweet-limit = "1">
			</a> 
			
			<script async src="https://platform.twitter.com/widgets.js" charset=
			"utf-8"></script>
			""",scrolling=True,height = 500
				) 
			st.caption("Vaccinate4Life") 

			st.write("")
			st.write("")  

			components.html("""<a class="twitter-timeline"
			href="https://twitter.com/MoHFW_INDIA" 
			data-tweet-limit = "1">
			</a> 
			
			<script async src="https://platform.twitter.com/widgets.js" charset=
			"utf-8"></script>
			""",scrolling=True,height = 500
				) 
			st.caption("Ministry of Health India Official")


		# News and tweets related to oxygen cylinders
		elif intent == 'oxygen_news':
			# Audio with the summary of the page
			st.audio("oxygen_news.wav")
			

			try:
				res = requests.get("https://api.rootnet.in/covid19-in/stats/latest")  
				res = res.json()
				res = res['data']['summary']
				total_cases = res['total']
				recovered = res['discharged']
				deaths = res['deaths']
				st.title("India Current Covid Stats:")
				st.markdown(f"<b>Total Cases</b>: {total_cases}",unsafe_allow_html=True)
				st.markdown(f"<b>Total Recovered</b>: {recovered}",unsafe_allow_html=True)
				st.markdown(f"<b>Total Deaths</b>: {deaths}",unsafe_allow_html=True)
			except:
				pass
			
			subscription_key = "7e1a2f7b90464dbd90e5a4e353e4b3fe"
			headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
			
			search_term = "Oxygen Cylinders News in India"
			
			search_url = "https://api.bing.microsoft.com/v7.0/news/search"
			params  = {"q": search_term, "textDecorations": True, "textFormat": "HTML","count":2}
			response = requests.get(search_url, headers=headers, params=params)
			response.raise_for_status()
			search_results = response.json()

			#st.json(search_results)

			if len(search_results['value'])>0:
				st.title("News Links:")
				for x in search_results['value']:
					st.markdown(f"<b>{cleanhtml(x['name'])}</b>",unsafe_allow_html=True)
					st.markdown(f"{cleanhtml(x['description'])}")
					try:
						st.image(f"{x['image']['thumbnail']['contentUrl']}",width=150)
					except:
						st.info("No Image found")
					st.markdown(f'<a href="{x["url"]}" target="_blank">Link</a>', unsafe_allow_html=True)
					
			else:   
				st.subheader("No relevant news available currently.")

			st.write("")
			st.write("")
			st.write("")
			
			
			# Fetch Top Tweets
			search_term = "Oxygen Cylinders Tweets Sellers"
			search_url = "https://api.bing.microsoft.com/v7.0/news/search"
			params  = {"q": search_term, "textDecorations": True, "textFormat": "HTML","count":1}
			response = requests.get(search_url, headers=headers, params=params)
			response.raise_for_status()
			search_results = response.json()

			components.html("""<a class="twitter-timeline"
			href="https://twitter.com/covidnewsbymib" 
			data-tweet-limit = "1">
			</a> 
			
			<script async src="https://platform.twitter.com/widgets.js" charset=
			"utf-8"></script>
			""",scrolling=True,height = 500
				)
			st.caption("Ministry of Information and Broadcasting")

			st.write("")
			st.write("")
			st.write("")

			components.html("""<a class="twitter-timeline"
			href="https://twitter.com/MoHFW_INDIA" 
			data-tweet-limit = "1">
			</a> 
			
			<script async src="https://platform.twitter.com/widgets.js" charset=
			"utf-8"></script>
			""",scrolling=True,height = 500
				) 
			st.caption("Ministry of Health India Official")           
					
			

		
		# Check Available Vaccine slots    
		# Ex: Please show vaccination slots available in Hyderabad
		elif intent == 'show_appointments':
			try:
				location = response['entities']['wit$location:location'][0]['body'].lower()
				d = pd.read_csv('district_ids.csv')

				# Process Dataframe
				loc_id = d[d['low_district_name']==location].iloc[0]['district_id']
				#print(loc_id)
				#st.write(loc_id)
			except:
				loc_id = 581

			st.audio("show_appointments.wav")	    

			

			temp = 0
			try:
				with st.spinner('Fetching appointments'):
					res = requests.get(f'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={loc_id}&date={date.today().strftime("%d-%m-%y")}')
					#st.markdown(res.ok)
					res = res.json()
					#st.json(res)       -  JSON returned from CoWin
					temp = 1
					st.info(f"State: {res['centers'][0]['state_name']} | District: {res['centers'][0]['district_name']}")
				
			
			except: 
				#st.info("Entered Alwar")
				with open('hyd_response.pkl','rb') as file:
					res = pickle.load(file)     
			

			# Process Output dataframe
			dictionary = {}
			identity = []
			name = []
			#state_name = []
			#district_name = []

			# Cache Response Case
			if temp == 0:
				st.info(f"State: Telangana | District: Hyderabad")

			block_name = []
			pincode = []
			timing = []
			fee_type = []
			date = []
			available_capacity = []
			age_limit = []
			vaccine = []
			res = res['centers']
			count = 0
			with st.spinner('Processing Appointments'):
				for x in res:
					identity.append(count)
					name.append(x['name'])
					#state_name.append(x['state_name'])
					#district_name.append(x['district_name'])
					block_name.append(x['block_name'])
					pincode.append(x['pincode'])
					timing.append(f"{x['from'][:5]} - {x['to'][:5]}")
					fee_type.append(x['fee_type'])
					date.append(x['sessions'][0]['date'])  # Fetching earliest appointment
					available_capacity.append(x['sessions'][0]['available_capacity'])
					#available_capacity.append(x['sessions'][0]['available_capacity'])
					age_limit.append(x['sessions'][0]['min_age_limit'])
					vaccine.append(x['sessions'][0]['vaccine'])
					count += 1

				dictionary['ID'] = identity
				dictionary['Name'] = name
				#dictionary['State'] = state_name
				#dictionary['District'] = district_name
				dictionary['Block Name'] = block_name
				dictionary['Pin'] = pincode
				dictionary['Date'] = date
				dictionary['Vaccine'] = vaccine
				dictionary['Capacity'] = available_capacity
				dictionary['Age Limit'] = age_limit
				dictionary['Timing'] = timing
				dictionary['Fees'] = fee_type

				#st.markdown((date))

				output_df = pd.DataFrame(dictionary)

				#st.table(output_df)
				st.subheader('Vaccination Slots Available')
				st.dataframe(output_df)
				output_df.to_csv('data_file.csv', index = False)

		
		# Only show first 10 rows
		elif intent == 'first_rows':
			# Audio which says only few rows are being displayed
			# and tell user how to show all rows
			try:
				output_df = pd.read_csv('data_file.csv')
				st.dataframe(output_df.head(10))
				st.caption('First 10 rows being displayed')
			except:
				st.info("Fetch appointments first.")    


		# Show all rows from dataframe
		elif intent == 'all_rows':
			# Audio which says all rows are being displayed
			# and prompts user to book apoointment
			try:
				output_df = pd.read_csv('data_file.csv')
				st.dataframe(output_df.sort_values(by='Capacity',ascending=False))
				st.caption('All rows being displayed')
				st.caption('Tip: Email relevant appointments to yourself.')                 
			except:
				st.info("Fetch appointments first.")    

		elif intent == 'app_details':
			st.audio("app_details.wav")
								   
			components.html("""Vaccino is a voice application powered by Graviton2 processor that strives
				to help people in India combat the fast spreading second wave
				of the corona virus.<br> <br>
				<b>Fetaures:</b>
				<ul>
				<li>Get important news related to <i>Vaccines</i> and <i>Oxygen Cylinders</i>.</li>
				<li>Fetch relevant Tweets from trusted sources.</li>
				<li>Show Vaccination slots available in a particular district and notify yourself.</li>
				</ul>
				<br>""")

				
			components.html("""<br><b>Privacy</b>: <br>
				No user data is stored. Your voice is used only to capture the intent and understand your need.
				All information shown has been retrieved from trusted and publicly available APIs like CoWin official API
				for vaccine slot booking.
				""")


		# Help/FAQs
		elif intent == 'help':
			st.audio("help.wav")
								  
			components.html("""You can try one of the following utterances:
				
				<li> What can you do? </li>
				<li> Why should I trust you? </li> 
				<li> Any information related to vaccines </li>
				<li> Fetch some details about status of oxygen cylinders in India </li>
				<li> Show vaccination appointments available in Alwar </li>
				<li> Email me the details of the appointments 1 and 21. </li>
				
				""")
		elif intent == '':
			st.info("Try saying 'Help me' to know what you can do")                          


  

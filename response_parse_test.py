_response = """|response|
I'm sorry to hear that. It's okay to feel that way. Maybe we can brainstorm some other games or activities you can do when you can't play chess with your mum.

|knowledge|
- My name is Sam
- My mum is in prison
- I have had a traumatic experience
- I enjoy playing chess, but can't play with my mum at the moment

|concern|
FALSE"""

response_key, response, knowledge_key, knowledge, concern_key, concern = [_.strip() for _ in _response.split("|")[1:]]
print({response_key: response,
       knowledge_key: [_.replace("- ", "") for _ in knowledge.split("\n")],
       concern_key: False if concern == 'FALSE' else True})
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.4",
    input="Say hello in one short sentence."
)

print(response.output_text)

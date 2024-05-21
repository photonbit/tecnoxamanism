import json
import click
from bs4 import BeautifulSoup
import os.path
from transformers import pipeline


class Message:
    def __init__(self, author, role, content, tags_limit, previous=None, tags=None):
        self.author = author
        self.role = role
        self.content = content
        self.tags_limit = tags_limit
        self.previous = previous
        self.tags = tags or []

    def assign_tags(self, nlp):
        model_response = nlp(
            f"Generate at most {self.tags_limit} tags from the given content: -----------\n{self.content}-----------\n")
        print(model_response[0]['generated_text'])
        # self.tags.extend(extracted_tags[:self.tags_limit])


def prune_tags(messages):
    for input_message, output_message in messages:
        common_tags = set(input_message.tags) & set(output_message.tags)
        input_message.tags = list(common_tags)
        output_message.tags = list(common_tags)


def convert_to_dict(file_path):
    extension = os.path.splitext(file_path)[1]

    with open(file_path, 'r') as file:
        file_content = file.read()

    if extension == '.html':
        # Use BeautifulSoup to parse HTML content
        soup = BeautifulSoup(file_content, 'html.parser')
        script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
        if not script_tag:
            click.echo("Could not find the JSON data in the HTML file.")
            return
        json_data = json.loads(script_tag.string)
    elif extension == '.json':
        print("A por el jotasón")
        json_data = json.loads(file_content)

    return json_data


def convert_to_markdown():
    json_data = convert_to_dict("983fb3c4-cbf0-4fd1-a1dd-b07af950a189.json")

    conversation_data = json_data['props']['pageProps']['serverResponse']['data']['linear_conversation']
    messages = []

    previous_message = None
    for item in conversation_data:
        if message := item.get('message'):
            if content := message.get('content'):
                text = content['parts'][0]
                author = message['author']['role']

                messages.append(
                    Message(author=author, role=author, content=text, tags_limit=3, previous=previous_message))
                previous_message = message

    # Process and tag messages
    # for message in messages:
    #    message.assign_tags(nlp)

    # Prune tags if needed
    # prune_tags([(messages[i], messages[i + 1]) for i in range(len(messages) - 1)])

    # Convert to Obsidian Markdown
    obsidian_output = convert_to_obsidian(messages)
    print(obsidian_output)

    # Write to file
    with open('conversation.md', 'w') as file:
        file.write(obsidian_output)


def convert_to_obsidian(messages):
    messages_md = []
    previous_message_link = None

    for index, message in enumerate(messages):
        tags_md = ' '.join([f'#{tag}' for tag in message.tags])
        author_link = f"[[{message.author}]]"
        message_id = f"Message_{index + 1}"
        message_link = f"[[{message_id}]]"

        message_md = f"### {message_link}\n**{author_link}**: {message.content} {tags_md}"
        if previous_message_link:
            message_md = f"{previous_message_link} → {message_md}"
        messages_md.append(message_md)

        previous_message_link = message_link

    return "\n\n".join(messages_md)


if __name__ == '__main__':
    convert_to_markdown()

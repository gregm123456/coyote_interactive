import json
import sys

def escape_backticks(content):
    return content.replace("```", "\\`\\`\\`")

def convert_conversation_to_md(conversation):
    md_content = []
    for entry in conversation:
        role = entry['role']
        content = escape_backticks(entry['content'])
        if role == 'system':
            md_content.append(f"**System Message:**\n\n{content}\n")
        elif role == 'user':
            md_content.append(f"**User:**\n\n{content}\n")
        elif role == 'assistant':
            md_content.append(f"**Assistant:**\n\n{content}\n")
    return "\n".join(md_content)

def main(input_file, output_file):
    with open(input_file, 'r') as f:
        conversation = json.load(f)
    
    md_content = convert_conversation_to_md(conversation)
    
    with open(output_file, 'w') as f:
        f.write(md_content)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python conversation_json_to_md.py <input_json_file> <output_md_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    main(input_file, output_file)

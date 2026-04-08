from data_dictionary_generator import generate_data_dictionary

def main() -> None:
    output_path = generate_data_dictionary()
    print(f"Generated data dictionary: {output_path}")

if __name__ == "__main__":
    main()
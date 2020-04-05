from app import create_app

app = create_app()

if __name__ == "__main__":
    context = ('divaexplorer-tvj_co_uk.crt', 'key.key')
    app.run(ssl_context=context, port=443)
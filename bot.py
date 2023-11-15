"""
WARNING:

Please make sure you install the bot with `pip install -e .` in order to get all the dependencies
on your Python environment.

Also, if you are using PyCharm or another IDE, make sure that you use the SAME Python interpreter
as your IDE.

If you get an error like:
```
ModuleNotFoundError: No module named 'botcity'
```

This means that you are likely using a different Python interpreter than the one used to install the bot.
To fix this, you can either:
- Use the same interpreter as your IDE and install your bot with `pip install --upgrade -r requirements.txt`
- Use the same interpreter as the one used to install the bot (`pip install --upgrade -r requirements.txt`)

Please refer to the documentation for more information at https://documentation.botcity.dev/
"""

# Import for the Web Bot
from botcity.web import WebBot, Browser, By

# Import for integration with BotCity Maestro SDK
from botcity.maestro import *
from botcity.web.util import element_as_select
from botcity.web.parsers import table_to_dict
from botcity.plugins.excel import BotExcelPlugin

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

excel = BotExcelPlugin()
excel.add_row(["Cidade","Número de Habitantes"])

def main():
    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    maestro = BotMaestroSDK.from_sys_args()
    ## Fetch the BotExecution with details from the task, including parameters
    execution = maestro.get_execution()

    #maestro.login(server="https://developers.botcity.dev",login="0d7f57cc-e88c-4cb7-97b8-1e3c7d7db300",key="0D7_YGECF1TME9XCRNOBZ2SJ")

    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    bot = WebBot()

    # Configure whether or not to run on headless mode
    bot.headless = False

    # Uncomment to change the default Browser to Firefox
    bot.browser = Browser.CHROME

    # Uncomment to set the WebDriver path
    bot.driver_path = r"C:\Users\julia\BotCityProjects\Botcity Arquivos\chromedriver.exe"

    # Opens the BotCity website.
    bot.browse(r"https://buscacepinter.correios.com.br/app/faixa_cep_uf_localidade/index.php")

    drop_uf = element_as_select(bot.find_element("//select[@id='uf']",By.XPATH))
    uf = "MG"
    drop_uf.select_by_value(uf)

    btn_search = bot.find_element("//button[@id='btn_pesquisar']", By.XPATH)
    btn_search.click()

    bot.wait(3000)

    tb_result = bot.find_element("//table[@id='resultado-DNEC']", By.XPATH)
    tb_result = table_to_dict(tb_result,has_header=True)

   
    bot.navigate_to(r"https://cidades.ibge.gov.br/brasil/sp/panorama")
    in_search_city = bot.find_element("//input[@placeholder='O que você procura?']", By.XPATH)

    str_last_city = ''

    cont = 1

    for row in tb_result:
        if cont <=10:
            city = row["localidade"]

            if(city == str_last_city):
                continue

            in_search_city.send_keys(city+" "+uf)
            opt_city = bot.find_element(f"//a[contains(span,'{city}')]", By.XPATH) # Fazer span robusto com estado ​f"//a[span[contains(text(), '{city}')] and span[contains(text(), {uf})]]"
            bot.wait(1000)

            opt_city.click()
            bot.wait(2000)

            population = bot.find_element("//div[@class='indicador__valor']", By.XPATH)
            str_population = population.text

            print(city+" "+str_population)
            excel.add_row([city, str_population])
            maestro.new_log_entry(activity_label="CIDADES", values={"CIDADE":f"{city}",
                                                                    "HABITANTES":f"{str_population}"})

            str_last_city = city
            cont+=1
        else:
            print("Quantidade alcançada")
            break

    excel.write(r"C:\Users\julia\BotCityProjects\Botcity Arquivos\ibge_cities.xlsx")

    # Implement here your logic...
    ...
   

    # Wait 3 seconds before closing
    bot.wait(3000)

    # Finish and clean up the Web Browser
    # You MUST invoke the stop_browser to avoid
    # leaving instances of the webdriver open
    bot.stop_browser()

    # Uncomment to mark this task as finished on BotMaestro
    # maestro.finish_task(
    #     task_id=execution.task_id,
    #     status=AutomationTaskFinishStatus.SUCCESS,
    #     message="Task Finished OK."
    # )


def not_found(label):
    print(f"Element not found: {label}")


if __name__ == '__main__':
    main()

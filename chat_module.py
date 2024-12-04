
@dp.message()
async def save_message(message: Message):
    bot_message = ''
    user_message = message.text

    sentiment = analyze_sentiment(user_message)
    

    write_in_file('messages.txt', f"Я: {message.text}\n")

    if contains_any_word(["удалить", "очистить", "удали"], user_message):
        await delete_message_data()
        await message.reply('История очищена', reply_markup=keyboard)

        write_in_file('messages.txt', f"Бот: {bot_message}\n")
        return

    if contains_any_word(["погода", "погодка", "температура", "погоды", "градусов"], user_message):
        city = find_next_word('в', str(user_message))
        bot_message = await get_weather_data(city)
        await message.reply(bot_message, reply_markup=keyboard)

        write_in_file('messages.txt', f"Бот: {bot_message}\n")
        return

    if contains_any_word(["валют", "валюты", "курс"], user_message):
        bot_message = await get_valute_data()
        await message.reply(bot_message, reply_markup=keyboard)

        write_in_file('messages.txt', f"Бот: {bot_message}\n")
        return

    if contains_any_word(["история", "историю"], user_message):
        bot_message = read_all_file('messages.txt')
        await message.reply(f"История сообщений:\n {bot_message}\n", reply_markup=keyboard)

        write_in_file('messages.txt', f"Бот: История сообщений:\n {bot_message}\n")
        return

    if contains_any_word(["история", "историю", "переписку"], user_message):
        bot_message = read_all_file('messages.txt')
        await message.reply(f"История сообщений:\n {bot_message}\n", reply_markup=keyboard)

        write_in_file('messages.txt', f"Бот: История сообщений:\n {bot_message}\n")
        return

    if contains_any_word(["здарова", "привет", "здорова"], user_message):
        await bot.send_message(message.chat.id, f"Здравствуйте, {message.chat.first_name}! \n")

        write_in_file('messages.txt', f"Здравствуйте\n")
        return

    if contains_any_word(["настроение"], user_message):
        await bot.send_message(message.chat.id, f"Ваше настроение я оцениваю {sentiment}.")

        write_in_file('messages.txt', f"Здравствуйте\n")
        return
# **** START HERE ****
#
# Write the system prompt that tells the LLM how to behave as a to-do assistant.
#
# The system prompt is the set of instructions you give the model BEFORE any user
# message. It shapes how the model interprets user input and what it does with it.
#
# Your prompt must tell the model to:
#
#   1. Act as a to-do list assistant.
#
#   2. Use the placeholder {TODAY} so the app can inject the current date at runtime.
#
#   3. Call the `add_task` tool whenever the user describes something that needs to
#      be done (reminders, errands, homework, chores, appointments, etc.).
#
#   4. Fill these exact fields when calling the tool:
#        - description (required): a plain-English restatement of the task.
#        - status: always "todo" unless the user says it is done or in progress.
#        - category: infer from context (e.g. work, personal, shopping, health).
#                    Use "" if unclear.
#        - people: comma-separated names mentioned in the task. Use "" if none.
#        - deadline: the date/time the user mentions. Use "" if none.
#                    NEVER invent a deadline.
#
#   5. NOT call any tool if the message is purely a greeting, a question with no
#      action, or small talk. In that case reply with plain text only.
#
#   6. Never call the tool more than once per message.
#
#   7. Never invent information that is not present in the user's message.
#
# Delete these comment lines and write your prompt below.
# ****  END HERE  ****

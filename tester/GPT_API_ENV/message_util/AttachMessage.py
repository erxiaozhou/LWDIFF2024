from typing import Optional


class AttachedChat:
    def __init__(self, role, message):
        self.role = role
        self.message = message.strip('\n ')
        
    def release_dict(self):
        return {
            'role': self.role,
            'content': self.message
        }

    @classmethod
    def from_system_role(cls, message):
        return cls('system', message)

    @classmethod
    def from_user_role(cls, message):
        return cls('user', message)

class AttachedChats:
    def __init__(self, chats:Optional[list[AttachedChat]]=None):
        if chats is None:
            chats = []
        self.chats = chats

    def append_chat(self, chat:AttachedChat):
        self.chats.append(chat)

    def release_messages(self):
        return [chat.release_dict() for chat in self.chats]


class AttachChatFactory:
    @staticmethod
    def start_system_setting():
        setting_msg = 'You are an expert in WebAssembly. Please answer the following question. You should first describe the answer in natural language and then provide the answer in JSON format.'
        return AttachedChat.from_system_role(setting_msg)
    # def __init__(self)


class AttachedChatsFactory:
    @staticmethod
    def generate_cfg_query_msg(mian_question, background)->AttachedChats:
        # raise NotImplementedError
        wrapped_background_msg = f'Here is some description about the control flow construct syntax: \n {background}'
        msgs = [
            AttachChatFactory.start_system_setting(),
            AttachedChat.from_system_role(wrapped_background_msg),
            AttachedChat.from_user_role(mian_question)
        ]
        return AttachedChats(msgs)

    @staticmethod
    def generate_inst_query_msg(main_question)->AttachedChats:
        msgs = [
            AttachChatFactory.start_system_setting(),
            AttachedChat.from_user_role(main_question)
        ]

        
        return AttachedChats(msgs)


    @staticmethod
    def generate_common_query_msg(main_question)->AttachedChats:
        msgs = [
            AttachChatFactory.start_system_setting(),
            AttachedChat.from_user_role(main_question),
#             AttachedChat.from_system_role('''Please check
# 1. Whether the response is correct?
# 1. Whether the response misuse the `list`, i.e., whether it represnt a Union as a list?
# 2. Whether the response misses any variations of the definition?''')
        ]
        return AttachedChats(msgs)
        raise NotImplementedError


    @staticmethod
    def generate_query_msg_with_refine(main_question, refine_info)->AttachedChats:
        msgs = [
            AttachChatFactory.start_system_setting(),
            AttachedChat.from_user_role(main_question),
            AttachedChat.from_user_role(refine_info),
            # AttachedChat.from_system_role('''Please ensure the response is correct and complete. The response should include all variations of the definition. Ensure the response does not misuse the `list` and (misuse meaning represent a Union as a list).''')
        ]
        return AttachedChats(msgs)
        raise NotImplementedError


def get_rethink_message_for_inst():
    return AttachedChat(
        'assistant',
        'Please re-check your answer, checking whether you consider the operations taken by the instruction and describe the possible execution behavior of the instruction in detail. For example, if a behavior is described by the text `The instruction traps if the absolute value computation is not defined.`, you should try to point out the conditions of instruciton input clearly, avoiding leaving the  field `InputConstraint` empty.'
    )


def ori_get_message(content, background):
    if background:
        messages=[
            {
                "role": "system",
                "content": 'You are an expert in WebAssembly.'
            },
            {
                "role": "system",
                "content": 'Here are some background information, including the description of operators, some operators maybe useful:\n ' + repr(background) + '\nIf the background information is unseless for you to answer the question, you can ignore it.',
            },
            {
                "role": "user",
                "content": content,
            }
        ]
    else:
        messages=[
            {
                "role": "system",
                "content": 'You are an expert in WebAssembly.'
            },
            {
                "role": "user",
                "content": content,
            }
        ]
        
    return messages

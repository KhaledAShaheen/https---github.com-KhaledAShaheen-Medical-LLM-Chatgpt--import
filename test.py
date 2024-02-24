import torch
import torch.optim as optim
from trl import SFTTrainer
from peft import LoraConfig
from datasets import load_dataset
from transformers import (AutoModelForCausalLM, AutoTokenizer, TrainingArguments, pipeline)

# Loading the model
llama_model = AutoModelForCausalLM.from_pretrained("aboonaji/llama2finetune-v2")
llama_model.config.use_cache = False
llama_model.config.pretraining_tp = 1

# Loading the tokenizer
llama_tokenizer = AutoTokenizer.from_pretrained("aboonaji/llama2finetune-v2", use_fast=True)
llama_tokenizer.pad_token = llama_tokenizer.eos_token
llama_tokenizer.padding_side = "right"

# Setting the training arguments
training_arguments = TrainingArguments(output_dir="./results", per_device_train_batch_size=4, max_steps=100)

# Creating the Supervised Fine-Tuning trainer
llama_sft_trainer = SFTTrainer(model=llama_model,
                               args=training_arguments,
                               train_dataset=load_dataset(path="aboonaji/wiki_medical_terms_llam2_format", split="train"),
                               tokenizer=llama_tokenizer,
                               peft_config=LoraConfig(task_type="CAUSAL_LM", r=64, lora_alpha=16, lora_dropout=0.1),
                               dataset_text_field="text")

# Training the model
llama_sft_trainer.train()

# Chatting with the model
user_prompt = "Please tell me about Bursitis"
text_generation_pipeline = pipeline(task="text-generation", model=llama_model, tokenizer=llama_tokenizer, max_length=300)
model_answer = text_generation_pipeline(f"<s>[INST] {user_prompt} [/INST]")
print(model_answer[0]['generated_text'])

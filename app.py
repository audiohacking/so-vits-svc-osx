import os
import subprocess
import yaml
import sys
import webbrowser
import gradio as gr
from ruamel.yaml import YAML
import shutil
import soundfile
import shlex

# UI strings: English only (no i18n/locale)

class WebUI:
    def __init__(self):
        self.train_config_path = 'configs/train.yaml'
        self.info = Info()
        self.names = []
        self.names2 = []
        self.voice_names = []
        self.base_config_path = 'configs/base.yaml'
        if not os.path.exists(self.train_config_path):
            shutil.copyfile(self.base_config_path, self.train_config_path)
            print("Initialization successful")
        else:
            print("Ready")
        self.main_ui()

    def main_ui(self):
        with gr.Blocks(theme=gr.themes.Base(primary_hue=gr.themes.colors.green)) as ui:

            gr.Markdown('# so-vits-svc5.0 WebUI')

            with gr.Tab("Preprocessing & Training"):

                with gr.Accordion("Training instructions", open=False):

                    gr.Markdown(self.info.train)

                gr.Markdown("### Preprocessing settings")

                with gr.Row():

                    self.model_name = gr.Textbox(value='sovits5.0', label='model', info='Model name', interactive=True)

                    self.f0_extractor = gr.Textbox(value='crepe', label='f0_extractor', info='F0 extractor', interactive=False)

                    self.thread_count = gr.Slider(minimum=1, maximum=os.cpu_count(), step=1, value=2, label='thread_count', info='Preprocessing thread count', interactive=True)

                gr.Markdown("### Training settings")

                with gr.Row():

                    self.learning_rate = gr.Number(value=5e-5, label='learning_rate', info='Learning rate', interactive=True)

                    self.batch_size = gr.Slider(minimum=1, maximum=50, step=1, value=6, label='batch_size', info='Batch size', interactive=True)

                with gr.Row():

                    self.info_interval = gr.Number(value=50, label='info_interval', info='Log interval (steps)', interactive=True)

                    self.eval_interval = gr.Number(value=1, label='eval_interval', info='Validation interval (epochs)', interactive=True)

                    self.save_interval = gr.Number(value=5, label='save_interval', info='Checkpoint save interval (epochs)', interactive=True)

                    self.keep_ckpts = gr.Number(value=0, label='keep_ckpts', info='Keep latest checkpoints (0 = keep all)', interactive=True)

                with gr.Row():

                    self.slow_model = gr.Checkbox(label="Add base model", value=True, interactive=True)

                gr.Markdown("### Start training")

                with gr.Row():

                    self.bt_open_dataset_folder = gr.Button(value='Open dataset folder')

                    self.bt_onekey_train = gr.Button('One-click training', variant="primary")

                    self.bt_tb = gr.Button('Start Tensorboard', variant="primary")

                gr.Markdown("### Resume training")

                with gr.Row():

                    self.resume_model = gr.Dropdown(choices=sorted(self.names), label='Resume training progress from checkpoints', info='Restore from checkpoint', interactive=True)

                    with gr.Column():

                        self.bt_refersh = gr.Button('Refresh')

                        self.bt_resume_train = gr.Button('Resume training', variant="primary")

            with gr.Tab("Inference"):

                with gr.Accordion("Inference instructions", open=False):

                    gr.Markdown(self.info.inference)

                gr.Markdown("### Inference settings")

                with gr.Row():

                    with gr.Column():

                        self.keychange = gr.Slider(-24, 24, value=0, step=1, label='Pitch shift')

                        self.file_list = gr.Markdown(value="", label="File list")

                        with gr.Row():

                            self.resume_model2 = gr.Dropdown(choices=sorted(self.names2), label='Select the model you want to export',
                                                             info='Select model to export', interactive=True)
                            with gr.Column():

                                self.bt_refersh2 = gr.Button(value='Refresh model and timbre')


                                self.bt_out_model = gr.Button(value='Export model', variant="primary")

                        with gr.Row():

                            self.resume_voice = gr.Dropdown(choices=sorted(self.voice_names), label='Select the sound file',
                                                            info='Select timbre file', interactive=True)

                        with gr.Row():

                            self.input_wav = gr.Audio(type='filepath', label='Select audio to convert', source='upload')

                        with gr.Row():

                            self.bt_infer = gr.Button(value='Start conversion', variant="primary")

                        with gr.Row():

                            self.output_wav = gr.Audio(label='Output audio', interactive=False)

            self.bt_open_dataset_folder.click(fn=self.openfolder)
            self.bt_onekey_train.click(fn=self.onekey_training,inputs=[self.model_name, self.thread_count,self.learning_rate,self.batch_size, self.info_interval, self.eval_interval,self.save_interval, self.keep_ckpts, self.slow_model])
            self.bt_out_model.click(fn=self.out_model, inputs=[self.model_name, self.resume_model2])
            self.bt_tb.click(fn=self.tensorboard)
            self.bt_refersh.click(fn=self.refresh_model, inputs=[self.model_name], outputs=[self.resume_model])
            self.bt_resume_train.click(fn=self.resume_train, inputs=[self.model_name, self.resume_model, self.learning_rate,self.batch_size, self.info_interval, self.eval_interval,self.save_interval, self.keep_ckpts, self.slow_model])
            self.bt_infer.click(fn=self.inference, inputs=[self.input_wav, self.resume_voice, self.keychange], outputs=[self.output_wav])
            self.bt_refersh2.click(fn=self.refresh_model_and_voice, inputs=[self.model_name],outputs=[self.resume_model2, self.resume_voice])

        server_port = int(os.environ.get('GRADIO_SERVER_PORT', 2333))
        native_app = os.environ.get('SOVITS_NATIVE_APP') == '1'
        ui.launch(inbrowser=not native_app, server_port=server_port, share=not native_app)

    def openfolder(self):

        try:
            if sys.platform.startswith('win'):
                os.startfile('dataset_raw')
            elif sys.platform.startswith('linux'):
                subprocess.call(['xdg-open', 'dataset_raw'])
            elif sys.platform.startswith('darwin'):
                subprocess.call(['open', 'dataset_raw'])
            else:
                print('Failed to open folder!')
        except BaseException:
            print('Failed to open folder!')

    def preprocessing(self, thread_count):
        print('Start preprocessing')
        train_process = subprocess.Popen('python -u svc_preprocessing.py -t ' + str(thread_count), stdout=subprocess.PIPE)
        while train_process.poll() is None:
            output = train_process.stdout.readline().decode('utf-8')
            print(output, end='')

    def create_config(self, model_name, learning_rate, batch_size, info_interval, eval_interval, save_interval,
                      keep_ckpts, slow_model):
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.width = 1024
        with open("configs/train.yaml", "r") as f:
            config = yaml.load(f)
        config['train']['model'] = model_name
        config['train']['learning_rate'] = learning_rate
        config['train']['batch_size'] = batch_size
        config["log"]["info_interval"] = int(info_interval)
        config["log"]["eval_interval"] = int(eval_interval)
        config["log"]["save_interval"] = int(save_interval)
        config["log"]["keep_ckpts"] = int(keep_ckpts)
        if slow_model:
            config["train"]["pretrain"] = "vits_pretrain\sovits5.0.pretrain.pth"
        else:
            config["train"]["pretrain"] = ""
        with open("configs/train.yaml", "w") as f:
            yaml.dump(config, f)
        return f"{config['log']}"

    def training(self, model_name):
        print('Start training')
        train_process = subprocess.Popen('python -u svc_trainer.py -c ' + self.train_config_path + ' -n ' + str(model_name), stdout=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_CONSOLE)
        while train_process.poll() is None:
            output = train_process.stdout.readline().decode('utf-8')
            print(output, end='')

    def onekey_training(self, model_name, thread_count, learning_rate, batch_size, info_interval, eval_interval, save_interval, keep_ckpts, slow_model):
        print(self, model_name, thread_count, learning_rate, batch_size, info_interval, eval_interval,
              save_interval, keep_ckpts)
        self.create_config(model_name, learning_rate, batch_size, info_interval, eval_interval, save_interval, keep_ckpts, slow_model)
        self.preprocessing(thread_count)
        self.training(model_name)

    def out_model(self, model_name, resume_model2):
        print('Start exporting model')
        try:
            subprocess.Popen('python -u svc_export.py -c {} -p "chkpt/{}/{}"'.format(self.train_config_path, model_name, resume_model2),stdout=subprocess.PIPE)
            print('Model exported successfully')
        except Exception as e:
            print("Error:", e)


    def tensorboard(self):
        if sys.platform.startswith('win'):
            tb_process = subprocess.Popen('tensorboard --logdir=logs --port=6006', stdout=subprocess.PIPE)
            webbrowser.open("http://localhost:6006")
        else:
            p1 = subprocess.Popen(["ps", "-ef"], stdout=subprocess.PIPE) #ps -ef | grep tensorboard | awk '{print $2}' | xargs kill -9
            p2 = subprocess.Popen(["grep", "tensorboard"], stdin=p1.stdout, stdout=subprocess.PIPE)
            p3 = subprocess.Popen(["awk", "{print $2}"], stdin=p2.stdout, stdout=subprocess.PIPE)
            p4 = subprocess.Popen(["xargs", "kill", "-9"], stdin=p3.stdout)
            p1.stdout.close()
            p2.stdout.close()
            p3.stdout.close()
            p4.communicate()
            tb_process = subprocess.Popen('tensorboard --logdir=logs --port=6007', stdout=subprocess.PIPE)
        while tb_process.poll() is None:
            output = tb_process.stdout.readline().decode('utf-8')
            print(output)

    def refresh_model(self, model_name):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_root = os.path.join(self.script_dir, f"chkpt/{model_name}")
        self.models_root = os.path.join(self.script_dir, f"models/{model_name}")
        print(self.models_root)
        print(self.model_root)
        self.names = []
        try:
            for self.name in os.listdir(self.model_root):
                if self.name.endswith(".pt"):
                    self.names.append(self.name)
            for self.name in os.listdir(self.models_root):
                if self.name.endswith(".pth"):
                    self.names.append(os.path.join("models", self.name))
            return {"choices": sorted(self.names), "__type__": "update"}
        except FileNotFoundError:
            return {"label": "Missing model file", "__type__": "update"}

    def refresh_model2(self, model_name):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_root = os.path.join(self.script_dir, f"chkpt/{model_name}")
        self.models_root = os.path.join(self.script_dir, f"models/{model_name}")
        print(self.models_root)
        print(self.model_root)
        self.names = []
        try:
            for self.name in os.listdir(self.model_root):
                if self.name.endswith(".pt"):
                    self.names.append(self.name)
            for self.name in os.listdir(self.models_root):
                if self.name.endswith(".pth"):
                    self.names.append(os.path.join("models", self.name))
            return {"choices": sorted(self.names), "__type__": "update"}
        except FileNotFoundError:
            return {"label": "Missing model file", "__type__": "update"}

    def refresh_voice(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_root = os.path.join(self.script_dir, "data_svc/singer")
        self.voice_names = []
        try:
            for self.name in os.listdir(self.model_root):
                if self.name.endswith(".npy"):
                    self.voice_names.append(self.name)
            return {"choices": sorted(self.voice_names), "__type__": "update"}
        except FileNotFoundError:
            return {"label": "Missing file", "__type__": "update"}

    def refresh_model_and_voice(self, model_name):
        model_update = self.refresh_model2(model_name)
        voice_update = self.refresh_voice()
        return model_update, voice_update

    def resume_train(self, model_name, resume_model ,learning_rate, batch_size, info_interval, eval_interval, save_interval, keep_ckpts, slow_model):
        print('Start resume training')
        self.create_config(model_name, learning_rate, batch_size, info_interval, eval_interval, save_interval,keep_ckpts, slow_model)
        train_process = subprocess.Popen('python -u svc_trainer.py -c {} -n {} -p "chkpt/{}/{}"'.format(self.train_config_path, model_name, model_name, resume_model), stdout=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_CONSOLE)
        while train_process.poll() is None:
            output = train_process.stdout.readline().decode('utf-8')
            print(output, end='')

    def inference(self, input, resume_voice, keychange):
        if os.path.exists("test.wav"):
            os.remove("test.wav")
            print("Residual files cleaned up")
        else:
            print("No residual files to clean")
        self.train_config_path = 'configs/train.yaml'
        print('Start inference')
        shutil.copy(input, ".")
        input_name = os.path.basename(input)
        os.rename(input_name, "test.wav")
        input_name = "test.wav"
        if not input_name.endswith(".wav"):
            data, samplerate = soundfile.read(input_name)
            input_name = input_name.rsplit(".", 1)[0] + ".wav"
            soundfile.write(input_name, data, samplerate)
        train_config_path = shlex.quote(self.train_config_path)
        keychange = shlex.quote(str(keychange))
        cmd = ["python", "-u", "svc_inference.py", "--config", train_config_path, "--model", "sovits5.0.pth", "--spk",
               f"data_svc/singer/{resume_voice}", "--wave", "test.wav", "--shift", keychange]
        train_process = subprocess.run(cmd, shell=False, capture_output=True, text=True)
        print(train_process.stdout)
        print(train_process.stderr)
        print("Inference complete")
        return "svc_out.wav"

class Info:
    def __init__(self) -> None:
        self.train = "### Credits: [@OOPPEENN](https://github.com/OOPPEENN), [@thestmitsuk](https://github.com/thestmitsuki)"
        self.inference = "### Credits: [@OOPPEENN](https://github.com/OOPPEENN), [@thestmitsuk](https://github.com/thestmitsuki)"


if __name__ == "__main__":
    webui = WebUI()

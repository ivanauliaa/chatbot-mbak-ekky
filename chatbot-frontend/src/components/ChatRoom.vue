<template>
<section>
  <div class="chat-box">
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Chatbot PENS</a>
      
        <b-link v-b-modal.modal-prevent-closing class="login-link" v-if="!isLoggedIn">Login</b-link>
        <b-link class="login-link" v-if="isLoggedIn" @click="logout">Logout</b-link>
        <b-modal
          id="modal-prevent-closing"
          ref="modal"
          title="Login Mahasiswa"
          @show="resetModal"
          @hidden="resetModal"
          @ok="handleOk"
          centered
        >
          <form ref="form" @submit.stop.prevent="handleSubmit" class="form-login">
            <b-form-group
              label="Name"
              label-for="name-input"
              invalid-feedback="Name is required"
              :state="nameState"
            >
              <b-form-input
                id="name-input"
                ref="nameForm"
                class="input"
                v-model="name"
                :state="nameState"
                required
                placeholder="Name"
              ></b-form-input>
            </b-form-group>
            <b-form-group
              label="NRP"
              label-for="nrp-input"
              invalid-feedback="NRP is required"
              :state="nrpState"
            >
              <b-form-input
                id="nrp-input"
                ref="nrpForm"
                class="input"
                v-model="nrp"
                :state="nrpState"
                required
                placeholder="NRP"
              ></b-form-input>
            </b-form-group>
          </form>
        </b-modal>
      </div>
  </nav>
  <div class="chat-room">
      <div class="chat-room-list-container" v-chat-scroll>
        <ul class="chat-room-list">
          <li class="message"
              v-for="(message, idx) in messages"
              :key="idx"
          >
            <p>
              <span :id="message.author">{{message.author}}</span>
              <br/>
              <pre :class="message.author">{{message.text}}</pre>
            </p>
          </li>
        </ul>
      </div>
      <div class="chat-inputs">
        <input type="text"
          v-model="message"
          @keyup.enter="sendMessage" 
          class="field-input"
          id="inputPassword" 
          placeholder="Type some text..." >
        <button @click="sendMessage">Send</button>  
      </div>
  </div>
  </div>
  
</section>
</template>

<script >

export default {
  name: 'ChatRoom',
  data: ()=>({
    message:'',
    messages:[],
    questionType:'',
    context:'',
    name: '',
    nrp:'',
    nameState: null,
    nrpState:null,
    submittedNames: [],
    submittedNRP: [],
    mahasiswa_id: null,
    isLoggedIn: false,
    path: "http://127.0.0.1:5000"
  }),
  created(){
    console.log('jalan')
      let msg = "Halo selamat datang di chatbot PENS! \nAjukan pertanyaan seputar peraturan akademik dan data mahasiswa (Jadwal, Nilai, Rekap presensi)"
      // this.$axios.get(this.this.path + "/greeting")
      // .then(res => {
      //     this.messages.push({
      //         text: res.data,
      //         author: 'chatbot-PENS'
      //     })
      // })

      this.messages.push({
          text: msg,
          author: 'chatbot-PENS'
      })

      msg = "Pilih jenis pertanyaan yang ingin anda ajukan : \n1. Pertanyaan umum / Peraturan akademik\n2. Data mahasiswa\n*(ketikkan \"ganti\" jika anda ingin mengganti jenis pertanyaan)"

      // this.$axios.get(this.path + "/question-type")
      // .then(res => {
      //     this.messages.push({
      //         text: res.data,
      //         author: 'chatbot-PENS'
      //     })
      // })
      this.messages.push({
          text: msg,
          author: 'chatbot-PENS'
      })

  },
  methods:{
    checkFormValidity() {
      const nameValid = this.$refs.nameForm.checkValidity()
      const nrpValid = this.$refs.nrpForm.checkValidity()
      this.nameState = nameValid
      this.nrpState = nrpValid
      if(nameValid && nrpValid)
        return true
      else
        return false
    },
    resetModal() {
      this.name = ''
      this.nrp = ''
      this.nameState = null
      this.nrpState = null
    },
    handleOk(bvModalEvent) {
      // Prevent modal from closing
      bvModalEvent.preventDefault()
      // Trigger submit handler
      this.handleSubmit()
    },
    handleSubmit() {
      // Exit when the form isn't valid
      if (!this.checkFormValidity()) {
        return
      }
      // Push the name to submitted names
      this.submittedNames.push(this.name)
      this.submittedNRP.push(this.nrp)
      // Hide the modal manually
      this.$nextTick(() => {
        this.login()
        this.$bvModal.hide('modal-prevent-closing')
      })
    },
    login(){
      const data = {
                    'name' : this.name,
                    'nrp' : this.nrp
                   }
      this.$axios.post(this.path + "/login", data)
      .then(res => {
          if(res.data.nomor == ''){
            this.messages.push({
                text: "Login gagal, periksa kembali Nama dan NRP anda",
                author: 'chatbot-PENS'
            })
          }else{
            this.mahasiswa_id = res.data.nomor
            this.isLoggedIn =  true
            this.messages.push({
                text: "Halo, " + res.data.nama,
                author: 'chatbot-PENS'
            })
            if(this.questionType == 'data mahasiswa'){
              let msg = "Tanyakan tentang nilai, jadwal, atau rekap absensi"
              this.messages.push({
                  text: msg,
                  author: 'chatbot-PENS'
              })
            }
          }
      })
    },
    logout(){
      this.mahasiswa_id = null
      this.isLoggedIn = false

      this.messages.push({
          text: "Anda berhasil logout",
          author: 'chatbot-PENS'
      })

      let msg = "Halo selamat datang di chatbot PENS! \nAjukan pertanyaan seputar peraturan akademik dan data mahasiswa (Jadwal, Nilai, Rekap presensi)"
      // this.$axios.get(this.this.path + "/greeting")
      // .then(res => {
      //     this.messages.push({
      //         text: res.data,
      //         author: 'chatbot-PENS'
      //     })
      // })

      this.messages.push({
          text: msg,
          author: 'chatbot-PENS'
      })
    
      msg = "Pilih jenis pertanyaan yang ingin anda ajukan : \n1. Pertanyaan umum / Peraturan akademik\n2. Data mahasiswa\n*(ketikkan \"ganti\" jika anda ingin mengganti jenis pertanyaan)"

      // this.$axios.get(this.path + "/question-type")
      // .then(res => {
      //     this.messages.push({
      //         text: res.data,
      //         author: 'chatbot-PENS'
      //     })
      // })
      this.messages.push({
          text: msg,
          author: 'chatbot-PENS'
      })
    },
    sendMessage(){

      this.messages.push({
        text: this.message,
        author : 'me'
      })

      if(this.message == 'ganti' || this.message == 'Ganti'){
        this.messages.push({
              text: "Anda mengganti jenis pertanyaan",
              author: 'chatbot-PENS'
        })
        let msg = "Pilih jenis pertanyaan yang ingin anda ajukan : \n1. Pertanyaan umum / Peraturan akademik\n2. Data mahasiswa\n*(ketikkan \"ganti\" jika anda ingin mengganti jenis pertanyaan)"

        // this.$axios.get(this.path + "/question-type")
        // .then(res => {
        //     this.messages.push({
        //         text: res.data,
        //         author: 'chatbot-PENS'
        //     })
        // })
        this.messages.push({
            text: msg,
            author: 'chatbot-PENS'
        })
        this.questionType = ''
      }else if(this.questionType === '' && (this.message === '1' || this.message === 'peraturan akademik' || this.message === 'Peraturan akademik'|| this.message === 'pertanyaan umum' || this.message === 'Pertanyaan umum')){
        let msg = {'content' : 'peraturan akademik'}
        this.$axios.post(this.path + "/response-akademik", msg)
        .then(res => {
            this.messages.push({
                text: res.data,
                author: 'chatbot-PENS' 
            })
        })
        this.questionType = 'aturan akademik'
      }else if (this.questionType === '' && (this.message === '2' || this.message === 'data mahasiswa' || this.message === 'Data mahasiswa')){
            if(this.mahasiswa_id == null){
              this.messages.push({
                  text: "Anda harus login terlebih dahulu",
                  author: 'chatbot-PENS'
              })
            }else{
              this.messages.push({
                  text: "Tanyakan tentang nilai, jadwal, atau rekap absensi",
                  author: 'chatbot-PENS'
              })
            }
            this.questionType = 'data mahasiswa'
      }else if (this.questionType === 'aturan akademik'){
        let msg = {'content' : this.message}
        this.$axios.post(this.path + "/response-akademik", msg)
        .then(res => {
            this.messages.push({
                text: res.data,
                author: 'chatbot-PENS'
            })
        })
      }else if(this.questionType === 'data mahasiswa'){
        let msg = {
                      'content' : this.context + " " + this.message,
                      'id' : this.mahasiswa_id
                    }
        this.$axios.post(this.path + "/response-data", msg)
        .then(res => {
            if(res.data.context !== null){
              this.context = res.data.context
            }else{
              this.context = ''
            }
            this.messages.push({
                text: res.data.response,
                author: 'chatbot-PENS'
            })
        })
      }else{
        this.messages.push({
            text: "Pilihan anda tidak terdaftar",
            author: 'chatbot-PENS'
        })
            
      }

      this.message=''
    }
  }
  
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="css">
.chat-room,
.chat-room-list{
  display: flex;
  flex-direction: column;
  list-style-type: none;
}

.chat-room-list-container{
  overflow-y: auto;
}

.navbar{
  border-radius: 10px 10px 0px 0px;
}

.chat-room-list{
  padding-left: 15px;
  padding-right: 15px;
  padding-top: 5px;
}

.chat-box{
  border: none;
  width: 70vw;
  border-radius: 10px;
  margin-left: auto;
  margin-right: auto;
  height: 85vh;
  padding-left: 0px;
  box-shadow: 0px 0px 15px grey;
  margin-top: 45px;
}

.chat-room{
  border: none;
  width: 70vw;
  margin-left: auto;
  margin-right: auto;
  height: 73vh;
  justify-content: space-between;
  padding-left: 0px;
}

.chat-inputs{
  display: flex;
  margin-left: 10px;
  margin-right: 10px;
  margin-top: 5px;
}

input{
  line-height: 2;
  width: 90%;
  border-radius: 15px;
  padding-left: 15px;
  margin-right: 10px;
  background-color:#dee2e6;
  border: none;
}

button{
  line-height: 2;
  width: 10%;
  border-radius: 15px;
  border: 1px solid blue;
  color: white;
  background: blue;
}

.me{
    padding: 9px;
    border-radius: 15px;
    background: blue;
    color: white;
    float: right;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 15px;
    text-align: right;
}
.chatbot-PENS{
    padding: 9px;
    background: #dee2e6;
    border-radius: 15px;
    float: left;
    text-align: left;
    max-width: 700px;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 15px;
}

pre {
    white-space: pre-wrap;       /* Since CSS 2.1 */
    white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
    white-space: -pre-wrap;      /* Opera 4-6 */
    white-space: -o-pre-wrap;    /* Opera 7 */
    word-wrap: break-word;       /* Internet Explorer 5.5+ */
}

.login-link{
  padding-right: 32px;
  text-decoration: none;
}

.input{
  border-radius: 5px;
  margin-bottom: 10px;
}

.form-login{
  margin-left: 5px;
}

#me{
  color: #999;
  font-weight: bold;
  font-size: 12px;
  float: right;
}

#chatbot-PENS{
  color: #999;
  font-weight: bold;
  font-size: 12px;
  float: left;
}

@media only screen and (max-width: 600px) {
  .chat-box {
    width: 100%;
    margin: none;
    margin-top: 0px;
    box-shadow: none;
  }

  .chat-room{
    margin: 0px;
    width: 100%;
    min-height:90vh;
  }

  .chatbot-PENS{
    max-width: 350px;
    overflow-wrap: break-word;
    word-wrap: break-word;
  }

  button{
    width: auto;
    padding-left: 20px;
    padding-right: 20px;
  }

  input{
    height: 48px;
  }

  .login-link{
    padding-right: 3px;
  }
}

</style>

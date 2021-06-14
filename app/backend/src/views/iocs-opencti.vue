<template>
    <div class="backend-content" id="content">
        <div class="column col-8 col-xs-12">
            <h3 class="s-title">Manage OpenCTI instances</h3>
            <ul class="tab tab-block">
                <li class="tab-item">
                    <a href="#" v-on:click="switch_tab('addopencti')" v-bind:class="{ active: tabs.addopencti }">Add instance</a>
                </li>
                <li class="tab-item">
                    <a href="#" v-on:click="switch_tab('instances')" v-bind:class="{ active: tabs.instances }">Existing instances</a>
                </li>
            </ul>
            <div v-if="tabs.addopencti">
                <div class="misp-form">
                    <label class="misp-label">Instance name</label><span></span>
                    <input class="form-input" type="text" placeholder="CYBERACME OpenCTI" v-model="openctiinst.name" required>
                    <label class="misp-label">Instance URL</label><span></span>
                    <input class="form-input" type="text" placeholder="https://opencti.cyberacme.com" v-model="openctinst.url" required>
                    <label class="misp-label">Authentication key</label><span></span>
                    <input class="form-input" type="text" placeholder="83114ab2-3570-493b-8caa-14ef1bcf8e9a" v-model="openctiinst.key" required>
                    <label class="misp-label">Verify certificate? </label><span></span>
                    <div style="flex:50%"><label class="form-switch">
                    <input type="checkbox" v-model="openctiinst.ssl">
                    <i class="form-icon"></i>
                    </label></div>
                </div>
                <button class="btn-primary btn col-12" v-on:click="add_instance()">Add OpenCTI instance</button>
                <div class="form-group" v-if="added">
                    <div class="toast toast-success">
                        ✓ OpenCTI instance added successfully.
                    </div>
                </div>
                <div class="form-group" v-if="error">
                    <div class="toast toast-error">
                        ✗ OpenCTI instance not added. {{error}}
                    </div>
                </div>
            </div>
            <div class="form-group" v-if="tabs.instances">
                <div v-if="instances.length">
                    <table class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Server</th>
                                <th>Authkey</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="i in instances" v-bind:key="i.id">
                                <td>{{ i.name }}</td>
                                <td>{{ i.url.replace('https://', '') .replace('http://', '') }}</td>
                                <td>{{ i.apikey.slice(0,5) }} [...] {{ i.apikey.slice(35,40) }}</td>
                                <td>
                                    <span v-if="i.connected" class="misp-online tooltip" :data-tooltip="i.lastsync">✓ ONLINE</span>
                                    <span v-else class="misp-offline tooltip" :data-tooltip="i.lastsync">⚠ OFFLINE</span>
                                </td>
                                <td><button class="btn btn-sm" v-on:click="delete_instance(i)">Delete</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div v-else>
                    <div class="empty">
                        <div v-if="loading">
                            <p class="empty-title h5">
                                <span class="loading loading-lg"></span>
                            </p>
                            <p class="empty-subtitle">Testing and loading your OpenCTI instances.</p>
                        </div>
                        <div v-else>
                            <p class="empty-title h5">No OpenCTI instance found.</p>
                            <p class="empty-subtitle">Do not hesitate to add a OpenCTI instance.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>

import axios from 'axios'

export default {
    name: 'manageopencti',   
    data() {
        return { 
            error:false,
            loading:false,
            added:false,
            openctiinst:{ name:'', url:'',key:'', ssl:false },
            instances:[],
            tabs: { "addopencti" : true, "instances" : false },
            jwt:""
        }
    },
    props: { },
    methods: {
        add_instance: function()
        {  
            this.added = false;
            this.error = false;
            if (this.openctiinst.name && this.openctiinst.url && this.openctiinst.key)
            {
                axios.post(`/api/opencti/add`, { data: { instance: this.openctiinst } }, { headers: {'X-Token': this.jwt} }).then(response => {
                    if(response.data.status){
                        this.added = true;
                    } else {
                        this.error = response.data.message;
                    }
                })
                .catch(err => (console.log(err)))
            }
        },
        delete_instance(elem)
        {
            axios.get(`/api/opencti/delete/${elem.id}`, { timeout: 10000, headers: {'X-Token': this.jwt} })
            .then(response => {
                if(response.data.status){
                    this.instances = this.instances.filter(function(el) { return el != elem; }); 
                }
            })
            .catch(err => (console.log(err)))
        },
        get_opencti_instances()
        {
            this.loading = true;
            this.instances = []
            axios.get(`/api/opencti/get_all`, { timeout: 10000, headers: {'X-Token': this.jwt} })
            .then(response => {
                if(response.data.results){
                    this.instances = response.data.results;
                    this.instances.forEach(e => { 
                        var lastsync = parseInt((Date.now()/1000 - e.lastsync) / 86400)
                        e.lastsync = (!lastsync)? "Synchronized today" : `Synchronized ${lastsync} day(s) ago`
                        } )
                }
                this.loading = false
            })
            .catch(err => (console.log(err)))
        },
        switch_tab: function(tab) {

            Object.keys(this.tabs).forEach(key => {
                if( key == tab ){
                    this.tabs[key] = true
                    if (key == "instances") this.get_opencti_instances();
                } else {
                    this.tabs[key] = false
                }
            });
        },
        get_jwt(){
            axios.get(`/api/get-token`, { timeout: 10000 })
                .then(response => {
                    if(response.data.token){
                        this.jwt = response.data.token
                    }
                })
            .catch(err => (console.log(err)))
        }
    },
    created: function() {
        this.get_jwt();
    }
}
</script>

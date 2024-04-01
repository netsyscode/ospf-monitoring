<template>
    <div>
       
    </div>
</template>
<script setup>
    import { useCookies } from '@vueuse/integrations/useCookies';
    const cookies = useCookies()
    console.log(cookies)

    function set(){
        cookies.set('name', 'value')
    }

    function get(){
        console.log(cookies.get('name'))
    }

    function remove(){
        cookies.remove('name')
    }

</script>
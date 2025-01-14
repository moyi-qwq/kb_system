const API_BASE_URL = 'http://localhost:8000';
const LAST_CONFIG_KEY = 'last_selected_config';

const { createApp, ref, reactive } = Vue;
const { ElMessage, ElMessageBox } = ElementPlus;

const app = createApp({
    setup() {
        const configNames = ref([]);
        const activeConfig = ref('');
        const keysList = ref([]);
        const searchPattern = ref('*');

        // 配置对话框
        const configDialog = reactive({
            visible: false,
            form: {
                name: '',
                host: 'localhost',
                port: 6379,
                password: ''
            }
        });

        // 添加配置选择对话框
        const configSelectDialog = reactive({
            visible: false,
            configs: []
        });

        // 当前配置信息
        const currentConfigInfo = ref({});

        // 修改创建数据对话框
        const createDialog = reactive({
            visible: false,
            activeTab: 'manual',
            form: {
                key: '',
                jsonItems: [],
                importData: ''
            }
        });

        // 查看数据对话框
        const viewDialog = reactive({
            visible: false,
            key: '',
            data: {},
            editingKey: '',
            editingValue: '',
            editingNewKey: '',  // 添加新的字段用于存储正在编辑的问题
            showEdit: false
        });

        // 搜索对话框
        const searchDialog = reactive({
            visible: false,
            collection: '',
            query: '',
            topK: 5,
            threshold: 0.5,
            searchTarget: 'question',  // 添加搜索目标，默认搜索问题
            results: []
        });

        const activeMenu = ref('database');
        const modelConfigs = ref([]);
        const modelDialog = reactive({
            visible: false,
            mode: 'create',  // 'create' 或 'view'
            form: {
                name: '',
                url: '',
                api_key: '',
                model_type: 'chat'
            }
        });

        // 添加当前选中的模型配置信息
        const currentModelConfig = ref({});

        // 加载配置列表
        const loadConfigs = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/database/configs`);
                const names = response.data.names;
                
                // 获取每个配置的详细信息
                const configPromises = names.map(name => 
                    axios.get(`${API_BASE_URL}/database/config/${name}`)
                );
                const configs = await Promise.all(configPromises);
                
                // 保存配置信息
                configSelectDialog.configs = configs.map(res => res.data.config);
                
                // 自动选择配置
                if (!activeConfig.value) {
                    const lastConfig = localStorage.getItem(LAST_CONFIG_KEY);
                    if (lastConfig && names.includes(lastConfig)) {
                        selectConfig(configSelectDialog.configs.find(c => c.name === lastConfig));
                    } else if (names.length > 0) {
                        // 选择字典序最小的配置
                        const firstConfig = configSelectDialog.configs.find(c => c.name === names.sort()[0]);
                        selectConfig(firstConfig);
                    }
                }
            } catch (error) {
                ElMessage.error('加载配置失败');
            }
        };

        // 列出键
        const listKeys = async () => {
            if (!activeConfig.value) return;
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/data/${activeConfig.value}`,
                    { params: { pattern: searchPattern.value } }
                );
                keysList.value = response.data.keys.map(key => ({ key }));
            } catch (error) {
                ElMessage.error('获取键列表失败');
            }
        };

        // 选择配置
        const handleConfigSelect = (name) => {
            activeConfig.value = name;
            listKeys();
        };

        // 显示配置对话框
        const showConfigDialog = () => {
            configDialog.form = {
                name: '',
                host: 'localhost',
                port: 6379
            };
            configDialog.visible = true;
        };

        // 保存配置
        const saveConfig = async () => {
            try {
                await axios.post(`${API_BASE_URL}/database/config`, configDialog.form);
                ElMessage.success('配置保存成功');
                configDialog.visible = false;
                await loadConfigs();
            } catch (error) {
                ElMessage.error('保存配置失败');
            }
        };

        // 显示配置选择对话框
        const showConfigSelectDialog = () => {
            configSelectDialog.visible = true;
        };

        // 选择配置
        const selectConfig = (config) => {
            activeConfig.value = config.name;
            currentConfigInfo.value = config;
            localStorage.setItem(LAST_CONFIG_KEY, config.name);
            configSelectDialog.visible = false;
            listKeys();
        };

        // 显示创建数据对话框
        const showCreateDialog = () => {
            createDialog.form = {
                key: '',
                jsonItems: [],
                importData: ''
            };
            createDialog.activeTab = 'manual';
            createDialog.visible = true;
        };

        // 添加 JSON 字段
        const addJsonItem = () => {
            createDialog.form.jsonItems.push({ key: '', value: '' });
        };

        // 删除 JSON 字段
        const removeJsonItem = (index) => {
            createDialog.form.jsonItems.splice(index, 1);
        };

        // 创建数据
        const createData = async () => {
            try {
                let newData = {};
                
                // 获取要添加的数据
                if (createDialog.activeTab === 'manual') {
                    // 手动添加模式
                    for (const item of createDialog.form.jsonItems) {
                        if (item.key.trim()) {
                            try {
                                newData[item.key] = JSON.parse(item.value);
                            } catch {
                                newData[item.key] = item.value;
                            }
                        }
                    }
                } else {
                    // 批量导入模式
                    try {
                        if (createDialog.form.importData) {
                            newData = JSON.parse(createDialog.form.importData);
                        } else {
                            ElMessage.error('请先导入数据');
                            return;
                        }
                    } catch (error) {
                        console.error('JSON解析错误:', error);
                        ElMessage.error('JSON格式错误');
                        return;
                    }
                }

                // 检查数据是否为空
                if (Object.keys(newData).length === 0) {
                    ElMessage.error('数据不能为空');
                    return;
                }

                try {
                    // 先尝试获取已有数据
                    const response = await axios.get(
                        `${API_BASE_URL}/data/${activeConfig.value}/${createDialog.form.key}`
                    );
                    
                    // 如果数据已存在，使用 PUT 请求更新数据
                    await axios.put(
                        `${API_BASE_URL}/data/${activeConfig.value}/${createDialog.form.key}`,
                        newData
                    );
                    ElMessage.success('数据更新成功');
                } catch (error) {
                    if (error.response && error.response.status === 404) {
                        // 如果数据不存在，使用 POST 请求创建新数据
                        await axios.post(
                            `${API_BASE_URL}/data/${activeConfig.value}/${createDialog.form.key}`,
                            newData
                        );
                        ElMessage.success('数据创建成功');
                    } else {
                        // 其他错误
                        throw error;
                    }
                }
                
                createDialog.visible = false;
                await listKeys();
            } catch (error) {
                console.error('操作数据错误:', error);
                ElMessage.error('操作数据失败');
            }
        };

        // 获取值
        const getValue = async (key) => {
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/data/${activeConfig.value}/${key}`
                );
                viewDialog.key = key;
                viewDialog.data = response.data.data;
                viewDialog.visible = true;
            } catch (error) {
                ElMessage.error('获取数据失败');
            }
        };

        // 删除键
        const deleteKey = async (key) => {
            try {
                await ElMessageBox.confirm(`确定要删除 ${key} 吗？`);
                await axios.delete(
                    `${API_BASE_URL}/data/${activeConfig.value}/${key}`
                );
                ElMessage.success('删除成功');
                listKeys();
            } catch (error) {
                if (error !== 'cancel') {
                    ElMessage.error('删除失败');
                }
            }
        };

        // 导出数据
        const exportData = async () => {
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/export/${activeConfig.value}`,
                    {
                        params: { pattern: searchPattern.value }
                    }
                );
                
                // 创建下载
                const blob = new Blob(
                    [JSON.stringify(response.data.data, null, 2)],
                    { type: 'application/json' }
                );
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${activeConfig.value}-export.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                ElMessage.success('数据导出成功');
            } catch (error) {
                console.error('导出错误:', error);
                ElMessage.error('导出数据失败');
            }
        };

        // 修改删除配置的方法
        const deleteConfig = async (config) => {
            try {
                await ElMessageBox.confirm(
                    `确定要删除配置 "${config.name}" 吗？`,
                    '删除确认',
                    {
                        confirmButtonText: '确定',
                        cancelButtonText: '取消',
                        type: 'warning'
                    }
                );

                // 直接调用后端API删除配置
                await axios.post(`${API_BASE_URL}/database/config/delete`, { name: config.name });
                
                // 如果删除的是当前选中的配置，清空选择
                if (activeConfig.value === config.name) {
                    activeConfig.value = '';
                    currentConfigInfo.value = {};
                    localStorage.removeItem(LAST_CONFIG_KEY);
                }
                
                ElMessage.success('配置删除成功');
                configSelectDialog.visible = false;  // 关闭选择对话框
                await loadConfigs();  // 重新加载配置列表
            } catch (error) {
                if (error !== 'cancel') {
                    console.error('删除配置失败:', error);
                    ElMessage.error('删除配置失败');
                }
            }
        };

        // 处理JSON文件
        const handleJsonFileChange = async (file) => {
            try {
                const content = await readFileContent(file.raw);
                try {
                    const data = JSON.parse(content);
                    createDialog.form.importData = content;
                    ElMessage.success('JSON文件解析成功');
                } catch (error) {
                    console.error('JSON解析错误:', error);
                    ElMessage.error('JSON格式错误');
                }
            } catch (error) {
                console.error('文件读取错误:', error);
                ElMessage.error('读取文件失败');
            }
        };

        // 处理普通文件
        const handleFileChange = async (file) => {
            try {
                const content = await readFileContent(file.raw);
                // 将文件内容添加到待导入数据中
                const fileName = file.name;
                const fileContent = content;
                
                // 如果是手动模式，添加为新字段
                if (createDialog.activeTab === 'manual') {
                    createDialog.form.jsonItems.push({
                        key: fileName,
                        value: fileContent
                    });
                } else {
                    // 如果是导入模式，添加到JSON数据中
                    const currentData = createDialog.form.importData ? 
                        JSON.parse(createDialog.form.importData) : {};
                    currentData[fileName] = fileContent;
                    createDialog.form.importData = JSON.stringify(currentData, null, 2);
                }
                
                ElMessage.success(`文件 ${fileName} 添加成功`);
            } catch (error) {
                ElMessage.error('读取文件失败');
            }
        };

        // 读取文件内容的辅助函数
        const readFileContent = (file) => {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = (e) => resolve(e.target.result);
                reader.onerror = (e) => reject(e);
                reader.readAsText(file);
            });
        };

        // 修改搜索数据方法
        const searchData = async () => {
            if (!searchDialog.collection || !searchDialog.query) {
                ElMessage.warning('请选择知识库并输入搜索内容');
                return;
            }
            
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/search/${activeConfig.value}`,
                    {
                        params: {
                            collection_key: searchDialog.collection,
                            query: searchDialog.query,
                            top_k: searchDialog.topK,
                            threshold: searchDialog.threshold,
                            search_key: searchDialog.searchTarget === 'question'  // 根据选择决定搜索目标
                        }
                    }
                );
                searchDialog.results = response.data.results;
            } catch (error) {
                console.error('搜索错误:', error);
                ElMessage.error('搜索失败');
            }
        };

        // 显示搜索对话框
        const showSearchDialog = () => {
            searchDialog.visible = true;
            searchDialog.collection = '';
            searchDialog.query = '';
            searchDialog.results = [];
        };

        // 添加集合选择变更处理方法
        const handleCollectionChange = (value) => {
            searchDialog.collection = value;
            searchDialog.results = [];
        };

        // 添加导航处理方法
        const handleMenuSelect = (index) => {
            activeMenu.value = index;
            if (index === 'model') {
                loadModelConfigs();
            }
        };

        // 加载模型配置
        const loadModelConfigs = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/model/configs`);
                modelConfigs.value = Object.entries(response.data.configs).map(([name, config]) => ({
                    name,
                    ...config
                }));
                await initCurrentModel();
            } catch (error) {
                console.error('加载模型配置失败:', error);
                ElMessage.error('加载模型配置失败');
            }
        };

        // 显示模型配置对话框 - 创建模式
        const showModelDialog = () => {
            modelDialog.mode = 'create';
            modelDialog.form = {
                name: '',
                url: '',
                api_key: '',
                model_type: 'chat'
            };
            modelDialog.visible = true;
        };

        // 查看模型配置详情
        const viewModelConfig = (config) => {
            modelDialog.mode = 'edit';  // 改为 'edit' 模式
            modelDialog.form = { 
                ...config,
                api_key: '********'  // 使用星号表示API密钥
            };
            modelDialog.visible = true;
        };

        // 修改保存模型配置方法
        const saveModelConfig = async () => {
            try {
                // 如果是编辑模式且API密钥是星号，则不更新API密钥
                if (modelDialog.mode === 'edit' && modelDialog.form.api_key === '********') {
                    const { api_key, ...configWithoutKey } = modelDialog.form;
                    await axios.post(`${API_BASE_URL}/model/config`, configWithoutKey);
                } else {
                    await axios.post(`${API_BASE_URL}/model/config`, modelDialog.form);
                }
                
                ElMessage.success('模型配置保存成功');
                modelDialog.visible = false;
                await loadModelConfigs();
            } catch (error) {
                console.error('保存模型配置失败:', error);
                ElMessage.error('保存模型配置失败');
            }
        };

        // 修改删除模型配置方法
        const deleteModelConfig = async (config) => {
            try {
                await ElMessageBox.confirm(`确定要删除模型配置 "${config.name}" 吗？`);
                await axios.post(`${API_BASE_URL}/model/config/delete`, { name: config.name });
                
                // 如果删除的是当前选中的模型，清空当前模型
                if (currentModelConfig.value?.name === config.name) {
                    currentModelConfig.value = {};
                }
                
                ElMessage.success('删除成功');
                await loadModelConfigs();
            } catch (error) {
                if (error !== 'cancel') {
                    console.error('删除模型配置失败:', error);
                    ElMessage.error('删除模型配置失败');
                }
            }
        };

        // 修改编辑值的方法
        const editValue = (key, value) => {
            viewDialog.editingKey = key;
            viewDialog.editingNewKey = key;  // 初始化编辑的问题为当前问题
            viewDialog.editingValue = JSON.stringify(value, null, 2);
            viewDialog.showEdit = true;
        };

        // 修改保存编辑的方法
        const saveEdit = async () => {
            try {
                let parsedValue;
                try {
                    parsedValue = JSON.parse(viewDialog.editingValue);
                } catch {
                    parsedValue = viewDialog.editingValue;
                }

                // 如果问题发生了改变
                if (viewDialog.editingKey !== viewDialog.editingNewKey) {
                    // 删除旧的问题
                    delete viewDialog.data[viewDialog.editingKey];
                    // 添加新的问题和回答
                    viewDialog.data[viewDialog.editingNewKey] = parsedValue;
                } else {
                    // 仅更新回答
                    viewDialog.data[viewDialog.editingKey] = parsedValue;
                }

                // 发送到服务器
                await axios.put(
                    `${API_BASE_URL}/data/${activeConfig.value}/${viewDialog.key}`,
                    viewDialog.data
                );

                viewDialog.showEdit = false;
                ElMessage.success('更新成功');
            } catch (error) {
                ElMessage.error('更新失败');
            }
        };

        // 添加删除键值对的方法
        const deleteKeyValue = async (key) => {
            try {
                await ElMessageBox.confirm(`确定要删除键 "${key}" 吗？`);
                
                // 删除本地数据
                delete viewDialog.data[key];

                // 更新到服务器
                await axios.put(
                    `${API_BASE_URL}/data/${activeConfig.value}/${viewDialog.key}`,
                    viewDialog.data
                );

                ElMessage.success('删除成功');
            } catch (error) {
                if (error !== 'cancel') {
                    ElMessage.error('删除失败');
                }
            }
        };

        // 添加新键值对的方法
        const addKeyValue = async () => {
            const newKey = 'new_key_' + Date.now();
            viewDialog.data[newKey] = '';
            editValue(newKey, '');
        };

        // 添加选择模型配置方法
        const selectModelConfig = async (config) => {
            try {
                await axios.post(`${API_BASE_URL}/model/current/${config.name}`);
                currentModelConfig.value = config;
                ElMessage.success(`已选择模型: ${config.name}`);
            } catch (error) {
                ElMessage.error('选择模型失败');
            }
        };

        // 修改初始化当前模型的方法
        const initCurrentModel = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/model/current`);
                currentModelConfig.value = response.data.model;
            } catch (error) {
                // 如果获取失败，静默处理，将当前模型设为空对象
                currentModelConfig.value = {};
            }
        };

        // 初始化
        loadConfigs();

        return {
            configNames,
            activeConfig,
            keysList,
            searchPattern,
            configDialog,
            createDialog,
            viewDialog,
            handleConfigSelect,
            showConfigDialog,
            saveConfig,
            listKeys,
            showCreateDialog,
            createData,
            getValue,
            deleteKey,
            exportData,
            configSelectDialog,
            currentConfigInfo,
            showConfigSelectDialog,
            selectConfig,
            addJsonItem,
            removeJsonItem,
            deleteConfig,
            handleJsonFileChange,
            handleFileChange,
            searchDialog,
            searchData,
            showSearchDialog,
            activeMenu,
            modelConfigs,
            modelDialog,
            handleMenuSelect,
            showModelDialog,
            saveModelConfig,
            deleteModelConfig,
            editValue,
            saveEdit,
            deleteKeyValue,
            addKeyValue,
            currentModelConfig,
            viewModelConfig,
            selectModelConfig,
            initCurrentModel
        };
    }
});

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
}

app.use(ElementPlus);
app.mount('#app'); 
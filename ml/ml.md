# ML-подпроект (ml)

Этот каталог содержит код OOTDiffusion и вспомогательные инструменты для виртуальной примерки одежды.

## Основные файлы

- **.gitignore** — список файлов и папок, которые игнорируются Git внутри подпроекта `ml`.
- **LICENSE** — лицензия, определяющая условия использования и распространения кода и моделей.
- **README.md** — основной README проекта OOTDiffusion с инструкциями по установке и запуску.
- **requirements.txt** — основной список зависимостей для запуска кода OOTDiffusion.
- **requirements-ci.txt** — зависимости для CI, используемые при автоматическом тестировании.
- **scripts/download_models.py** — скрипт для скачивания необходимых предобученных моделей и контрольных точек.

## Clean Architecture

Актуальная структура ML-модуля теперь разделена по слоям:

- `swipeit_ml/domain` — сущности и enum'ы инференса.
- `swipeit_ml/application` — порты, use case и mask-логика.
- `swipeit_ml/infrastructure/adapters` — адаптеры к OpenPose, Parsing и OOTDiffusion.
- `swipeit_ml/infrastructure/config` — конфигурация checkpoint/runtime-путей.
- `swipeit_ml/infrastructure/runtime` — bootstrap путей и runtime helpers.
- `swipeit_ml/presentation` — presentation layer c CLI и demo.
- `third_party` — внешний legacy/vendor-код OOTDiffusion, отделённый от наших CA-слоёв.

## Папка `swipeit_ml/domain/`

- **entities.py** — входная модель запроса и результат инференса.
- **enums.py** — enum'ы `ModelType`, `GarmentCategory` и вспомогательные функции нормализации.

## Папка `swipeit_ml/infrastructure/adapters/`

- **openpose_adapter.py** — адаптер к OpenPose.
- **parsing_adapter.py** — адаптер к human parsing.
- **diffusion_adapter.py** — адаптер к OOTDiffusion.

## Папка `swipeit_ml/infrastructure/config/`

- **checkpoints.py** — правила разрешения путей к checkpoint'ам.

## Папка `swipeit_ml/infrastructure/runtime/`

- **paths.py** — bootstrap `sys.path` и вычисление runtime-путей проекта.

## Папка `images/`

- **demo.png** — пример результата работы модели.
- **workflow.png** — схема рабочего процесса и компонентов.

## Папка `third_party/ootd/` (ядро модели)

- **inference_ootd.py** — скрипт для запуска инференса модели в стандартном (half-body) сценарии.
- **inference_ootd_dc.py** — инференс для полного тела (Dress Code) с категорией одежды.
- **inference_ootd_hd.py** — инференс для модели высокой чёткости (HD).

### `third_party/ootd/pipelines_ootd/`

- **attention_garm.py** — модуль внимания для гардеробного (garment) потока.
- **attention_vton.py** — модуль внимания для общего VTON-потока.
- **pipeline_ootd.py** — главный класс пайплайна, связывающий все стадии обработки.
- **transformer_garm_2d.py** — 2D-трансформер для обработки данных гардероба.
- **transformer_vton_2d.py** — 2D-трансформер для VTON-процесса.
- **unet_garm_2d_blocks.py** — блоки U-Net для гардеробного потока.
- **unet_garm_2d_condition.py** — условная генерация для гардероба.
- **unet_vton_2d_blocks.py** — блоки U-Net для VTON-потока.
- **unet_vton_2d_condition.py** — условная генерация для VTON.

## Интеграция с backend

ML-пайплайн подключается к backend через [backend/app/infrastructure/ml/ootd_service.py](/Users/egor/Desktop/Diplom/backend/app/infrastructure/ml/ootd_service.py), а не через отдельный сервис внутри каталога `ml`.

## Папка `third_party/preprocess/` (предобработка данных)

### `third_party/preprocess/humanparsing/` — сегментация человека и разметка частей тела

- **parsing_api.py** — обёртка/интерфейс для вызова процедуры парсинга.
- **run_parsing.py** — скрипт для запуска парсинга изображений и сохранения результатов.

#### `third_party/preprocess/humanparsing/datasets/`

- **datasets.py** — классы для загрузки и подготовки данных.
- **simple_extractor_dataset.py** — упрощённый датасет для вырезания нужных частей.
- **target_generation.py** — генерация целевых меток/масок для обучения.

#### `third_party/preprocess/humanparsing/mhp_extension/` — расширения для Multi-Human Parsing

- **logits_fusion.py** — слияние логитов от нескольких моделей/уровней.
- **make_crop_and_mask_w_mask_nms.py** — обрезка и генерация масок с NMS.

##### `third_party/preprocess/humanparsing/mhp_extension/coco_style_annotation_creator/`

- **human_to_coco.py** — конвертация разметки человека в COCO-формат.
- **pycococreatortools.py** — утилиты для создания COCO-аннотаций.
- **test_human2coco_format.py** — тесты конвертации разметки.

##### `third_party/preprocess/humanparsing/mhp_extension/global_local_parsing/`

- **global_local_datasets.py** — датасеты для глобального/локального подхода.
- **global_local_evaluate.py** — оценка качества парсинга.
- **global_local_train.py** — скрипт для обучения модели глобально/локально.
- **make_id_list.py** — генерация списков идентификаторов образцов.

##### `third_party/preprocess/humanparsing/mhp_extension/scripts/`

- **make_coco_style_annotation.sh** — скрипт для создания COCO-разметки.
- **make_crop.sh** — скрипт для вырезания участков изображения.
- **parsing_fusion.sh** — скрипт для объединения результатов парсинга.

#### `third_party/preprocess/humanparsing/modules/` — сборка модулей нейронных сетей

- **bn.py** — модули нормализации (BatchNorm) с расширениями.
- **deeplab.py** — реализация модели DeepLab для сегментации.
- **dense.py** — полносвязные слои и блоки.
- **functions.py** — вспомогательные функции (активации, нормализации и т.п.).
- **misc.py** — прочие утилиты и вспомогательные классы.
- **residual.py** — остаточные блоки (ResNet-подобные).
- **src/** — дополнительный исходный код и зависимости.

#### `third_party/preprocess/humanparsing/networks/` — архитектуры

- **AugmentCE2P.py** — расширенная архитектура CE2P для парсинга.

##### `third_party/preprocess/humanparsing/networks/backbone/`

- **mobilenetv2.py** — MobileNetV2 backbone.
- **resnet.py** — ResNet backbone.
- **resnext.py** — ResNeXt backbone.

##### `third_party/preprocess/humanparsing/networks/context_encoding/`

- **aspp.py** — ASPP (Atrous Spatial Pyramid Pooling).
- **ocnet.py** — OCNet модуль.
- **psp.py** — PSPNet (Pyramid Scene Parsing).

#### `third_party/preprocess/humanparsing/utils/` — утилиты для обучения и оценки

- **consistency_loss.py** — потеря консистентности между предсказаниями.
- **criterion.py** — критерии/функции потерь.
- **encoding.py** — кодирование/декодирование меток.
- **kl_loss.py** — KL-дивергенция.
- **lovasz_softmax.py** — функция потерь Lovasz-Softmax.
- **miou.py** — метрика mIoU для сегментации.
- **schp.py** — шаблоны для SCHP (Self-correction for Human Parsing).
- **soft_dice_loss.py** — потеря Soft Dice.
- **transforms.py** — трансформации для изображений и масок.
- **warmup_scheduler.py** — планировщик шага обучения с warmup.

### `third_party/preprocess/openpose/` — извлечение поз

- **run_openpose.py** — скрипт запуска OpenPose для извлечения поз.
- **annotator/** — модуль для аннотирования и визуализации поз.

## Папка `swipeit_ml/presentation/` — presentation layer

- **gradio_demo.py** — реальная demo-точка входа.
- **cli.py** — реальная CLI-точка входа.

## Папка `examples/`

- **garment/** — образцы одежды.
- **model/** — примеры путей к моделям и конфигурациям.

Поддерживаемые entrypoint'ы после очистки:

- backend вызывает `backend/app/infrastructure/ml/ootd_service.py`
- CLI-инференс идёт через `swipeit_ml/presentation/cli.py`
- demo остаётся в `swipeit_ml/presentation/gradio_demo.py`

## Папка `tests/`

- **unit/** — быстрые unit-тесты domain/application/services.
- **integration/** — интеграционные тесты entrypoint'ов, адаптеров и сквозного use case.

### `tests/unit/`

- **test_run_ootd_inference.py** — unit-тест основного use case.
- **test_masking.py** — unit-тесты mask-логики.

### `tests/integration/`

- **test_run_ootd_inference_flow.py** — интеграционный сценарий инференса через временные файлы.
- **test_adapters_and_entry.py** — интеграционные тесты адаптеров и CLI.
- **test_gradio_module.py** — импорт и smoke-check Gradio demo.

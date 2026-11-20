import { createBackendModule } from '@backstage/backend-plugin-api';
import { scaffolderActionsExtensionPoint } from '@backstage/plugin-scaffolder-node';
import { createFileAction } from '../actions/createFileAction';

/**
 * Registers the custom scaffolder actions with the scaffolder plugin.
 *
 * Custom actions are contributed through the scaffolder's extension point
 * rather than being imported by the scaffolder itself, which is how the new
 * backend system keeps plugins and their extensions decoupled.
 */
export const scaffolderModuleCustomActions = createBackendModule({
  pluginId: 'scaffolder',
  moduleId: 'custom-actions',
  register(reg) {
    reg.registerInit({
      deps: { scaffolder: scaffolderActionsExtensionPoint },
      async init({ scaffolder }) {
        scaffolder.addActions(createFileAction());
      },
    });
  },
});

export default scaffolderModuleCustomActions;
